import argparse
import sys
from manage import StackManager


def create_help(header, options):
    """Create formated help."""
    return "\n" + header + "\n" + \
           "\n".join(map(lambda x: "  " + x, options)) + "\n"


def get_confirmation(prompt):
    """Method to confirm decisions
    Args:
        prompt(str): Question to ask the user
    Returns:
        (bool): True indicating yes, False indicating no
    """
    decision = False
    while True:
        confirm = raw_input("{} (y/n): ".format(prompt))
        if confirm.lower() == "y":
            decision = True
            break
        elif confirm.lower() == "n":
            decision = False
            break
        else:
            print("Enter 'y' or 'n' for 'yes' or 'no'")

    return decision


def main():
    actions = ["create", "update", "update_frontend", "delete", "populate"]
    actions_help = create_help("action supports the following:", actions)

    stack = ["dean", "production"]
    stack_help = create_help("stack supports the following:", stack)

    parser = argparse.ArgumentParser(description="Deployment Automation for DonateMates",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=actions_help + stack_help)
    parser.add_argument("action",
                        choices=actions,
                        metavar="action",
                        help="Action to execute")
    parser.add_argument("stack_name", help="Stack in which to execute the configuration (example: production)")

    args = parser.parse_args()

    mgr = StackManager(args.stack_name)

    if args.action.lower() == "create":
        # Create a stack
        if get_confirmation("Are you sure you want to create the Stack '{}'?".format(args.stack_name)):
            mgr.create()
        else:
            print("Create cancelled!")
    elif args.action.lower() == "update":
        # Update a stack
        mgr.update()
    elif args.action.lower() == "update_frontend":
        # Update just the frontend
        mgr.update_frontend()
    elif args.action.lower() == "delete":
        # Delete a stack
        if get_confirmation("Are you sure you want to delete the Stack '{}'?".format(args.stack_name)):
            mgr.delete()
        else:
            print("Delete cancelled!")
    elif args.action.lower() == "populate":
        # Pre-populate a stack
        if get_confirmation("Are you sure you want to populate the Stack '{}'?".format(args.stack_name)):
            mgr.populate()
        else:
            print("Populate cancelled!")
    else:
        print("Unsupported action: {}".format(args.action))
        sys.exit(1)

if __name__ == '__main__':
    main()
