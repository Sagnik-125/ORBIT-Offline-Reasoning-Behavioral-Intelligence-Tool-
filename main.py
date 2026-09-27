from llm import route_intent, chat_llama
from tools import search_item, open_item


def main():

    print("=" * 50)
    print("               ORBIT")
    print("       Local AI Desktop Assistant")
    print("=" * 50)
    print("Type 'exit' to close ORBIT.\n")

    while True:

        # ----------------------------------------------------
        # GET USER INPUT
        # ----------------------------------------------------

        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print("ORBIT: Goodbye!")
            break

        if not user_input:
            continue


        # ----------------------------------------------------
        # STEP 1: UNDERSTAND THE USER'S REQUEST
        # ----------------------------------------------------

        print("ORBIT: Thinking...")

        intent = route_intent(user_input)

        request_type = intent.get("type")
        action = intent.get("action")
        target_name = intent.get("target_name")


        # ----------------------------------------------------
        # STEP 2: NORMAL CONVERSATION
        # ----------------------------------------------------

        if request_type == "conversation":

            reply = chat_llama(user_input)

            print(f"ORBIT: {reply}")


        # ----------------------------------------------------
        # STEP 3: DESKTOP ACTION
        # ----------------------------------------------------

        elif request_type == "tool":

            # Currently supported opening actions
            if action in (
                "open_file",
                "open_folder",
                "open_app"
            ):

                # Check whether Llama extracted a target
                if not target_name:

                    print(
                        "ORBIT: I know you want to open something, "
                        "but I didn't catch the name."
                    )

                    continue


                # Search for the target
                print(
                    f"ORBIT: Looking for "
                    f"'{target_name}'..."
                )

                target = search_item(target_name)


                # Target wasn't found
                if target is None:

                    print(
                        f"ORBIT: I couldn't find "
                        f"'{target_name}' on your system."
                    )

                    continue


                # Target found
                print(
                    f"ORBIT: Found it at -> {target}"
                )


                # Ask Windows to open it
                success = open_item(target)


                if success:

                    print(
                        "ORBIT: Opened successfully."
                    )

                else:

                    print(
                        "ORBIT: I found it, but Windows "
                        "wouldn't let me open it."
                    )


            # Tool recognized, but not implemented
            else:

                print(
                    f"ORBIT: I detected a tool request "
                    f"('{action}'), but I don't know "
                    "how to perform it yet."
                )


        # ----------------------------------------------------
        # STEP 4: UNKNOWN REQUEST
        # ----------------------------------------------------

        else:

            print(
                "ORBIT: I couldn't understand "
                "that request."
            )


if __name__ == "__main__":
    main()