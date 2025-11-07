import os
import sys
from typing import List, Tuple
from dotenv import load_dotenv
from rag_engine import RAGEngine


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


def handle_add(engine, args):
    if not args:
        print("❌ Usage: /add <path>")
        return

    file_path = args[0]

    try:
        engine.add_document(file_path)
    except Exception as e:
        print(f"❌ Add failed: {str(e)}")
    else:
        print(f"✅ Added successfully: {file_path}")


def handle_remove(engine, args):
    if not args:
        print("❌ Usage: /remove <filename>")
        return

    filename = args[0]

    try:
        engine.remove_document(filename)
    except Exception as e:
        print(f"❌ Removal failed: {str(e)}")
    else:
        print(f"✅ Removal successful: {filename}")


def handle_list(engine):
    file_names = engine.list_files()

    if not file_names:
        print("No documents added")
    else:
        print(f"\n📜 Your Documents:")
        for file_name in file_names:
            print(f"- {file_name}")
        print()


def handle_reset(engine):
    files = engine.list_files()

    if not files:
        print("No documents added")
        return

    # Ask for confirmation
    print(f"⚠️ This will remove all {len(files)} document(s) and chat history ⚠️")
    confirm = input("Are you sure? (yes/no): ").strip()

    if confirm == "yes":
        try:
            engine.reset_all()
        except Exception as e:
            print(f"❌ Reset operation failed: {str(e)}")
        else:
            print(f"✅ Reset operation successful")


def handle_chat(engine, message):
    docchat_message = "\n🤖 Doc-Chat: "

    response, sources = engine.chat(message)
    docchat_message += response

    if sources:
        docchat_message += "\n\n📚 Sources:\n"
        for i in range(len(sources)):
            docchat_message += f"  [{i+1}] {sources[i]['source']} (Chunk {sources[i]['chunk_index']})\n"

    print(docchat_message)


def main() -> None:
    # Load environment variables
    load_dotenv()

    # Get OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        sys.exit(1)

    # Initialize RAG engine
    try:
        engine = RAGEngine(openai_api_key=api_key)
    except Exception as e:
        print(f"❌ Error initializing Doc-Chat: {str(e)}")
        sys.exit(1)

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
                    handle_add(engine, args)

                elif command == "remove":
                    handle_remove(engine, args)

                elif command == "list":
                    handle_list(engine)

                elif command == "reset":
                    handle_reset(engine)

                else:
                    print(f"❌ Unknown command: /{command}")

            # Handle chat message
            else:
                handle_chat(engine, user_input)

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
