from langserve import RemoteRunnable
import argparse

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Get a joke on any topic")
    parser.add_argument(
        "--topic",
        type=str,
        default="programming",
        help="Topic for the joke (default: programming)"
    )
    args = parser.parse_args()

    # Connect to the remote chain
    remote_chain = RemoteRunnable("http://localhost:8000/joke-generator/")

    # Invoke the chain with the topic
    print(f"\nGenerating a joke about '{args.topic}'...\n")
    response = remote_chain.invoke({"topic": args.topic})

    # Display the joke
    print("Here's your joke:")
    print("-" * 50)
    print(response)
    print("-" * 50)

if __name__ == "__main__":
    main()
