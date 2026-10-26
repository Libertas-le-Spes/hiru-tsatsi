import argparse

from hiru_tsatsi.wiring import Services


def add_workspace(services: Services, chosen: argparse.Namespace) -> int:
    services.edit.add_workspace(chosen.workspace, chosen.label)
    return 0


def change_workspace(services: Services, chosen: argparse.Namespace) -> int:
    services.edit.change_workspace(chosen.workspace, chosen.new_number, chosen.label)
    return 0


def remove_workspace(services: Services, chosen: argparse.Namespace) -> int:
    services.edit.remove_workspace(chosen.workspace)
    return 0


def add_app(services: Services, chosen: argparse.Namespace) -> int:
    services.edit.add_app(chosen.workspace, chosen.name, chosen.command)
    return 0


def change_app(services: Services, chosen: argparse.Namespace) -> int:
    services.edit.change_app(chosen.workspace, chosen.index, chosen.name, chosen.command)
    return 0


def remove_app(services: Services, chosen: argparse.Namespace) -> int:
    services.edit.remove_app(chosen.workspace, chosen.index)
    return 0


def choose_window(services: Services, chosen: argparse.Namespace) -> int:
    services.edit.choose_window(chosen.workspace, chosen.index, chosen.address)
    return 0


def forget_window(services: Services, chosen: argparse.Namespace) -> int:
    services.edit.forget_window(chosen.workspace, chosen.index)
    return 0
