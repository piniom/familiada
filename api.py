
from openai import OpenAI
import ast
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")
client = OpenAI(api_key=API_KEY)

SYSTEM_PROMPT = (
    "**Prompt:** Stwórz agenta unifikującego odpowiedzi z ankiety do formatu gry Familiada. Zasady:\n"
    "1. Grupuj odpowiedzi o zbliżonym, nawet odległym znaczeniu, zastępując je najprostszym wspólnym mianownikiem (np. \"lody pistacjowe\" → \"lody\", \"gra na gitarze\" → \"muzyka\").\n"
    "2. Ignoruj: wielkość liter, formy gramatyczne, dodatkowe określenia i przymiotniki.\n"
    "3. Zachowaj oryginalną kolejność, wybieraj najkrótsze możliwe formy (np. \"oglądanie seriali\" → \"seriale\").\n"
    "4. Agresywnie upraszczaj i uogólniaj znaczenia - liczba kategorii powinna wynosić około 5.\n"
    "5. Upewnij się, że każda odpowiedź wejściowa ma odpowiadającą jej odpowiedź wyjściową.\n"
    '6. Format wyjściowy: ["odp1", "odp2", ...] bez dodatkowych elementów.\n\n'
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

def single_question(question, answers):
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
        print("Lengths differ!")
    
    return response

def main():
    answers = ["terenowy", "wyścigowy", "jeep", "szybki", "formuła-1", "osobowy", "cięzarowka", "tir", "tir", "ciezarowka", "rodzinny"]
    response = single_question("Jaki jest najlepszy samochód?", answers)
    print(response)

def prompt_question( answers):
    prompt = f"Wejście: [{', '.join(answers)}] \n Wyjście:"
    return prompt
    


if __name__ == "__main__":
    main()