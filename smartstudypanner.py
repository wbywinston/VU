
"""
Smart Study Planner
--------------------
A console-based Python programme that helps a student log, review and
analyse their study sessions across different subjects over the course
of a semester. Data persists across runs in a file called
'study_log.txt'.

Author: <your name here>
"""

import os

DATA_FILE = "study_log.txt"
DELIMITER = "|"  # used to separate fields when saving/loading sessions


# ---------------------------------------------------------------------
# (c) classify_session(duration)
# ---------------------------------------------------------------------
def classify_session(duration):
    """
    Classify a study session based on its duration (in minutes).

    Short  -> under 30 minutes
    Medium -> 30 to 90 minutes (inclusive)
    Long   -> over 90 minutes
    """
    if duration < 30:
        return "Short"
    elif duration <= 90:
        return "Medium"
    else:
        return "Long"


# ---------------------------------------------------------------------
# (b) add_session()
# ---------------------------------------------------------------------
def add_session(sessions):
    """
    Prompt the user for details of a new study session, validate the
    duration, and append the session (as a dictionary) to the sessions
    list.
    """
    print("\n--- Add a Study Session ---")
    subject = input("Enter subject name: ").strip()
    topic = input("Enter topic covered: ").strip()
    date = input("Enter date or day label (e.g. 2026-09-03 or Monday): ").strip()

    # Keep re-prompting until a valid positive number is entered
    duration = None
    while duration is None:
        raw_duration = input("Enter duration of session (minutes): ").strip()
        try:
            value = float(raw_duration)
            if value <= 0:
                print("Duration must be a positive number. Please try again.")
                continue
            duration = value
        except ValueError:
            print("Invalid input. Please enter a numeric value for duration.")

    session = {
        "subject": subject,
        "topic": topic,
        "date": date,
        "duration": duration,
    }
    sessions.append(session)
    print(f"Session added successfully! ({classify_session(duration)} session)")


# ---------------------------------------------------------------------
# (d) view_sessions()
# ---------------------------------------------------------------------
def view_sessions(sessions):
    """
    Display every logged session in a neatly formatted table, including
    its Short/Medium/Long classification.
    """
    print("\n--- All Study Sessions ---")
    if not sessions:
        print("No sessions have been logged yet.")
        return

    header = f"{'Subject':<15}{'Topic':<20}{'Date':<15}{'Duration(min)':<15}{'Type':<10}"
    print(header)
    print("-" * len(header))
    for s in sessions:
        classification = classify_session(s["duration"])
        print(
            f"{s['subject']:<15}{s['topic']:<20}{s['date']:<15}"
            f"{s['duration']:<15.1f}{classification:<10}"
        )


# ---------------------------------------------------------------------
# (e) search_by_subject(subject)
# ---------------------------------------------------------------------
def search_by_subject(sessions, subject=None):
    """
    Let the user search for sessions belonging to a specific subject
    (case-insensitive). Displays matching sessions and the total time
    spent on that subject. If no sessions are found, a clear message
    is shown instead of an empty table.
    """
    print("\n--- Search Sessions by Subject ---")
    if subject is None:
        subject = input("Enter subject to search for: ").strip()

    matches = [s for s in sessions if s["subject"].lower() == subject.lower()]

    if not matches:
        print(f"No sessions found for subject '{subject}'.")
        return

    header = f"{'Subject':<15}{'Topic':<20}{'Date':<15}{'Duration(min)':<15}{'Type':<10}"
    print(header)
    print("-" * len(header))
    total_time = 0
    for s in matches:
        classification = classify_session(s["duration"])
        print(
            f"{s['subject']:<15}{s['topic']:<20}{s['date']:<15}"
            f"{s['duration']:<15.1f}{classification:<10}"
        )
        total_time += s["duration"]

    print(f"\nTotal time spent on '{subject}': {total_time:.1f} minutes "
          f"({total_time / 60:.2f} hours)")


# ---------------------------------------------------------------------
# (f) study_statistics()
# ---------------------------------------------------------------------
def study_statistics(sessions):
    """
    Compute and display:
      - total hours studied overall
      - total hours studied per subject
      - the subject with the least total study time (weakest area)
      - the single longest session recorded
    """
    print("\n--- Study Statistics ---")
    if not sessions:
        print("No sessions have been logged yet. Add a session first.")
        return

    total_minutes = sum(s["duration"] for s in sessions)
    print(f"Total hours studied overall: {total_minutes / 60:.2f} hours")

    # Total per subject
    per_subject = {}
    for s in sessions:
        per_subject[s["subject"]] = per_subject.get(s["subject"], 0) + s["duration"]

    print("\nTotal hours studied per subject:")
    for subject, minutes in per_subject.items():
        print(f"  {subject:<15}: {minutes / 60:.2f} hours")

    # Weakest subject (least total study time)
    weakest_subject = min(per_subject, key=per_subject.get)
    print(f"\nWeakest area (least total study time): {weakest_subject} "
          f"({per_subject[weakest_subject] / 60:.2f} hours)")

    # Longest single session
    longest = max(sessions, key=lambda s: s["duration"])
    print(f"\nLongest single session: {longest['subject']} - {longest['topic']} "
          f"({longest['duration']:.1f} minutes, "
          f"{classify_session(longest['duration'])})")


# ---------------------------------------------------------------------
# (g) save_sessions() and load_sessions()
# ---------------------------------------------------------------------
def save_sessions(sessions, filename=DATA_FILE):
    """
    Save every logged session to a text file. Each session is stored
    on its own line, with fields separated by DELIMITER.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for s in sessions:
                line = DELIMITER.join(
                    [s["subject"], s["topic"], s["date"], str(s["duration"])]
                )
                f.write(line + "\n")
        print(f"Sessions saved to '{filename}'.")
    except OSError as e:
        print(f"Error saving sessions: {e}")


def load_sessions(filename=DATA_FILE):
    """
    Load sessions from a text file if it exists. If the file does not
    exist (e.g. on the very first run), return an empty list instead
    of crashing.
    """
    sessions = []
    if not os.path.exists(filename):
        return sessions  # first run - nothing to load yet

    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(DELIMITER)
                if len(parts) != 4:
                    continue  # skip malformed lines rather than crash
                subject, topic, date, duration_str = parts
                try:
                    duration = float(duration_str)
                except ValueError:
                    continue  # skip malformed lines rather than crash
                sessions.append(
                    {
                        "subject": subject,
                        "topic": topic,
                        "date": date,
                        "duration": duration,
                    }
                )
    except OSError as e:
        print(f"Error loading sessions: {e}")

    return sessions


# ---------------------------------------------------------------------
# (a) Menu-driven interface
# ---------------------------------------------------------------------
def display_menu():
    print("\n===== Smart Study Planner =====")
    print("1. Add a study session")
    print("2. View all sessions")
    print("3. Search sessions by subject")
    print("4. View statistics")
    print("5. Save and exit")
    print("================================")


def main():
    sessions = load_sessions()  # automatically reload existing data
    print("Welcome to the Smart Study Planner!")
    if sessions:
        print(f"Loaded {len(sessions)} previous session(s) from '{DATA_FILE}'.")

    while True:
        display_menu()
        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            add_session(sessions)
        elif choice == "2":
            view_sessions(sessions)
        elif choice == "3":
            search_by_subject(sessions)
        elif choice == "4":
            study_statistics(sessions)
        elif choice == "5":
            save_sessions(sessions)
            print("Goodbye! Keep up the good study habits.")
            break
        else:
            # Reject invalid menu choices without crashing
            print("Invalid choice. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main()
