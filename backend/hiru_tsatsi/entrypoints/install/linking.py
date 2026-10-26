from hiru_tsatsi.use_cases.installing import LinkCommands


def link_commands(linking: LinkCommands) -> None:
    linked = linking.run()
    if linked.retired is not None:
        print(f"removed:  {linked.retired}, the old short name; type 'tsatsi' now")
    print(f"command:  {linked.command}, and {linked.short} for short")
