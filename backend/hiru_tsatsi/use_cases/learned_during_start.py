from dataclasses import dataclass

from hiru_tsatsi.use_cases.failures import ChangedMeanwhile
from hiru_tsatsi.use_cases.ports import AppListStore
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.app_list import AppList
from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.refusals import NothingThere


@dataclass(frozen=True)
class Learned:
    before: Placement
    after: App


def learned_between(before: AppList, after: AppList) -> list[Learned]:
    learned = []
    for placement in before.placements():
        now = after.placement(placement.workspace, placement.index).app
        if now != placement.app:
            learned.append(Learned(placement, now))
    return learned


def still_the_same_app(apps: AppList, placement: Placement) -> bool:
    try:
        return apps.placement(placement.workspace, placement.index).app == placement.app
    except NothingThere:
        return False


def applied_to(apps: AppList, learned: list[Learned]) -> AppList:
    for change in learned:
        if still_the_same_app(apps, change.before):
            apps = apps.with_app_replaced(change.before, change.after)
    return apps


def save_learned(store: AppListStore, before: AppList, after: AppList) -> None:
    if after == before:
        return
    try:
        store.save(after)
    except ChangedMeanwhile:
        store.save(applied_to(store.load(), learned_between(before, after)))
