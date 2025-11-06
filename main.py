import os
import sys
from typing import List, Tuple
from dotenv import load_dotenv


def print_help() -> None:
    print("\n📖 Commands:")
    print("  /add <path>     - Add a document to chat with")
    print("  /remove <name>  - Remove a document")
    print("  /list           - List all your documents")
    print("  /reset          - Remove all documents and chat history")
    print("  /help           - Show this help message")
    print("  /exit           - Quit the application")
    print("\nTo chat, just type your message\n")


def print_welcome() -> None:
    title = "📜 Welcome to Doc-Chat 🔎"
    print("\n" + "=" * len(title))
    print(title)
    print("=" * len(title))
    print_help()


def parse_command(user_input: str) -> Tuple[bool, str, List[str]]:
    user_input = user_input.strip()

    if not user_input.startswith("/"):
        return False, user_input, []

    parts = user_input[1:].split(" ", maxsplit=1)
    command = parts[0]

    args = []
    if len(parts) > 1:
        args.append(parts[1].strip())

    return True, command, args


def main() -> None:
    # Load environment variables
    load_dotenv()

    # Get OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        sys.exit(1)

    # Initialize RAG engine
    # TODO

    # Print welcome message
    print_welcome()

    # Main loop
    while True:
        try:
            user_input = input("> ").strip()

            if not user_input:
                continue

            # Parse input
            is_command, command, args = parse_command(user_input)

            # Handle commands
            if is_command:
                if command == "exit":
                    print("\n👋 Thanks for using Doc-Chat!")
                    break

                elif command == "help":
                    print_help()

                elif command == "add":
                    # TODO: handle_add()
                    pass

                elif command == "remove":
                    # TODO: handle_remove()
                    pass

                elif command == "list":
                    # TODO: handle_list()
                    pass

                elif command == "reset":
                    # TODO: handle_reset()
                    pass

                else:
                    print(f"❌ Unknown command: /{command}")

            # Handle chat message
            else:
                # TODO: handle_chat()
                pass

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
