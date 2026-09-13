
import json
import os
from pathlib import Path
from datetime import datetime


# ========================================
# CONFIGURATION
# ========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIRECTORY = str(PROJECT_ROOT / "data")

LOG_FILE = os.path.join(
    LOG_DIRECTORY,
    "learning_log.json"
)


# ========================================
# INITIALIZE LOG FILE
# ========================================

def initialize_log():
    """
    Create the data directory and learning
    log file if they do not already exist.
    """

    os.makedirs(
        LOG_DIRECTORY,
        exist_ok=True
    )

    if not os.path.exists(LOG_FILE):

        with open(
            LOG_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                [],
                file,
                indent=4
            )


# ========================================
# LOAD LEARNING LOG
# ========================================

def load_learning_log():
    """
    Load all learning records from the
    JSON learning log.
    """

    initialize_log()

    try:

        with open(
            LOG_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except (
        json.JSONDecodeError,
        FileNotFoundError
    ):

        return []


# ========================================
# SAVE LEARNING LOG
# ========================================

def save_learning_log(records):
    """
    Save learning records to the JSON file.
    """

    initialize_log()

    with open(
        LOG_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            indent=4,
            ensure_ascii=False
        )


# ========================================
# ADD LEARNING RECORD
# ========================================

def add_learning_record(
    user_message,
    ai_response,
    feedback=None,
    learning=None,
    evaluation_score=None
):
    """
    Store one complete AI learning interaction.
    """

    records = load_learning_log()

    record = {
        "timestamp": datetime.now().isoformat(
            timespec="seconds"
        ),

        "user_message": user_message,

        "ai_response": ai_response,

        "feedback": feedback,

        "learning": learning,

        "evaluation_score": evaluation_score
    }

    records.append(record)

    save_learning_log(records)

    return record


# ========================================
# GET LEARNING HISTORY
# ========================================

def get_learning_history():
    """
    Return the complete learning history.
    """

    return load_learning_log()


# ========================================
# GET LAST RECORD
# ========================================

def get_last_learning_record():
    """
    Return the most recent learning record.
    """

    records = load_learning_log()

    if not records:
        return None

    return records[-1]


# ========================================
# GET LEARNING SUMMARY
# ========================================

def get_learning_summary():
    """
    Generate basic statistics from the
    learning history.
    """

    records = load_learning_log()

    total = len(records)

    good = 0
    bad = 0

    scores = []

    for record in records:

        feedback = record.get(
            "feedback"
        )

        if feedback == "good":
            good += 1

        elif feedback == "bad":
            bad += 1

        score = record.get(
            "evaluation_score"
        )

        if isinstance(
            score,
            (int, float)
        ):

            scores.append(score)

    if scores:

        average_score = (
            sum(scores)
            / len(scores)
        )

    else:

        average_score = None

    return {
        "total_interactions": total,
        "positive_feedback": good,
        "negative_feedback": bad,
        "average_evaluation_score": average_score
    }


# ========================================
# TEST
# ========================================

if __name__ == "__main__":

    print(
        "================================"
    )

    print(
        "       MEMORY AI LEARNING LOG"
    )

    print(
        "================================"
    )

    print(
        "\nTesting learning log..."
    )

    record = add_learning_record(
        user_message="Test message",
        ai_response="Test response",
        feedback="good",
        learning="User likes clear responses.",
        evaluation_score=5
    )

    print(
        "\nRecord added:"
    )

    print(
        json.dumps(
            record,
            indent=4
        )
    )

    print(
        "\nLearning summary:"
    )

    summary = get_learning_summary()

    print(
        json.dumps(
            summary,
            indent=4
        )
    )

    print(
        "\nLearning log working successfully!"
    )