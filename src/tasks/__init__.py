from .email_classify import EmailClassifyTask
from .email_respond import EmailRespondTask
from .email_thread import EmailThreadTask

TASK_REGISTRY = {
    "email_classify": EmailClassifyTask,
    "email_respond": EmailRespondTask,
    "email_thread": EmailThreadTask,
}
