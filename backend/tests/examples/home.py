from hiru_tsatsi.work_apps.recognising import Recognising

HOME = "/home/sam"


def as_written(folder: str) -> str:
    return folder


RECOGNISING = Recognising(HOME, as_written)
