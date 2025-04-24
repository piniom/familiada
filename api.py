
from openai import OpenAI
import ast
from dotenv import load_dotenv
import os
import csv
from collections import Counter

load_dotenv()
API_KEY = os.getenv("API_KEY")
client = OpenAI(api_key=API_KEY)

def main():
    questions = load_file("responses.csv")

    with open('processed.txt', mode='w', buffering=1) as outputfile:
        for (question, answers) in questions:
            try:
                answers = single_question(questions, answers)
                answers = calculate_percentage(answers)
                answers = [(normalize_reply(question, a), p) for (a, p) in answers]
                outputfile.write(question + '\n')
                outputfile.write('\n'.join([f"    {a} {p}" for (a, p) in answers]) + '\n\n')
                outputfile.flush()
            except:
                print("\n".join([
                    "Error while processing question!"
                    f"Question: {question}"
                    f"Answers: {answers}"
                    ""
                ]))

def load_file(path):
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

        column_data = []

        for col_idx in range(1, len(rows[0])):  # Loop through each column
            column_values = [rows[row_idx][col_idx] for row_idx in range(len(rows)) if rows[row_idx][col_idx]]

            if column_values:
                first_cell = column_values[0]
                rest_of_column = column_values[1:]
                column_data.append((first_cell, rest_of_column))
        return column_data
    

def calculate_percentage(strings):
    total = len(strings)
    counts = Counter(strings)
    result = [(string, round((count / total) * 100)) for string, count in counts.items()]
    return sorted(result, key=lambda x: x[1], reverse=True)

def single_question(question, answers, retry = 0):
    SYSTEM_PROMPT = (
        "**Prompt:** Stwórz agenta unifikującego odpowiedzi z ankiety do formatu gry Familiada. Zasady:\n"
        "1. Grupuj odpowiedzi o zbliżonym, nawet odległym znaczeniu, zastępując je najprostszym wspólnym mianownikiem (np. \"lody pistacjowe\" → \"lody\", \"gra na gitarze\" → \"muzyka\").\n, unikaj abstrakcyjnych nazw stawiając na konkrety"
        "2. Ignoruj: wielkość liter, formy gramatyczne, dodatkowe określenia i przymiotniki.\n"
        "3. Zachowaj oryginalną kolejność, wybieraj raczej krótsze formy.\n"
        "4. Upraszczaj i uogólniaj znaczenia - całkowita liczba kategorii powinna wynosić około 5.\n, zostawiaj nazwy własne jedynie uwspólniając zapis, np. GOT ~ Gra o tron"
        "5. Upewnij się, że każda odpowiedź wejściowa ma odpowiadającą jej odpowiedź wyjściową.\n"
        '6. Format wyjściowy: ["odp1", "odp2", ...] bez dodatkowych elementów.\n\n'
        "7. Upewnij się, że każda odpowiedź wejściowa ma odpowiadającą jej odpowiedź wyjściową i ich liczba się zgadza\n"
        "8. Gdy pytanie jest o konkretną rzecz lub np. film czy ksiąkę, nie upraszczaj nazw własnych\n"
        "**Przykłady (skrócone - stąd mniejsza liczba kategorii):**  \n"
        "Wejście: [jabłuszko, biegać, chodzenie na spacery, maraton]  \n"
        'Wyjście: ["jabłka", "bieganie", "spacery", "bieganie"]  \n\n'
        "Wejście: [Netflix, oglądanie filmów, seriale, kino]  \n"
        'Wyjście: ["rozrywka", "filmy", "seriale", "filmy"]  \n\n'
        "Wejście: [gitara, pianino, śpiew, słuchanie muzyki]  \n"
        'Wyjście: ["muzyka", "muzyka", "muzyka", "muzyka"]  \n\n'
        "Wejście: [McDonald's, pizza, gotowanie obiadu, kebab]  \n"
        'Wyjście: ["jedzenie", "jedzenie", "gotowanie", "jedzenie"]  \n'
    )
    def prompt_question( answers):
        prompt = f"Wejście: [{', '.join(answers)}] \n Wyjście:"
        return prompt

    prompt = prompt_question( answers)
    
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        store=True,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        stream=True,
        temperature=0
    )
    response = ast.literal_eval("".join([chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content]))

    if len(answers) != len(response):
        if retry > 0:
            print(f"Lengths differ! \n{answers} \n{response}\nretrying {retry} \n\n")
            return single_question(question, answers, retry - 1)
        else: 
            print(f"Lengths differ! \n{answers} \n{response}\nFatal\n\n")

    
    return response

def normalize_reply(question, answer):
    SYSTEM_PROMPT = (
        "Dostając zapytanie w formie: \n" 
        "<pytanie>? <odp>"
        "Dostosuj odpowiedź by była gramatycznie i logicznie spójna z pytaniem \n"
        "Odpowiedź powinna być krótka, najlepiej 1 lub 2 słowa gdy jest taka mozliwosc"
        "Nie powtarzaj pytania ani oryginalnej odpowiedzi, tylko nowa odpowiedz"
        "\n**Przykład**\n"
        "Pytanie: Gdzie jest koloseum? Rzym\n"
        "**Twoja odpowiedź:**\n"
        "W Rzymie\n\n"
    )

    prompt = f"Pytanie: {question} \n A: {answer}\n"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            store=True,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            stream=True,
            temperature=0
        )
        response = "".join([chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content])
        return response
    except:
        print(f"Error while normalizing: {question} {answer}")
        return answer
    


if __name__ == "__main__":
    main()