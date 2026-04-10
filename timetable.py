import random
from collections import defaultdict

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


# ---------- TIME HELPERS ----------
def generate(start, end, breaks, courses):
    return generate_timetable(start, end, breaks, courses)
def to_minutes(t):
    h, m = map(int, t.split(":"))
    return h * 60 + m


def to_time(m):
    return f"{m//60:02d}:{m%60:02d}"


# ---------- INPUT ----------
def get_input():
    start = to_minutes(input("Start Time (HH:MM): "))
    end = to_minutes(input("End Time (HH:MM): "))

    num_breaks = int(input("\nNumber of breaks: "))
    breaks = []

    for i in range(num_breaks):
        print(f"\nBreak {i+1}")
        b_start = to_minutes(input("Break Start (HH:MM): "))
        b_dur = int(input("Break Duration (minutes): "))
        breaks.append((b_start, b_start + b_dur))

    num_tables = int(input("\nNumber of timetable sets: "))

    courses = []
    while True:
        name = input("\nCourse Name (or 'done'): ")
        if name.lower() == "done":
            break

        duration = int(input("Class duration (minutes): "))
        weekly = int(input("Classes per week: "))
        teachers = input("Teachers (comma separated): ").split(",")

        courses.append({
            "name": name,
            "duration": duration,
            "weekly": weekly,
            "teachers": [t.strip() for t in teachers]
        })

    return start, end, breaks, num_tables, courses


# ---------- BUILD TIME SLOTS ----------
def build_slots(start, end, breaks, duration):
    slots = []
    current = start

    while current + duration <= end:
        next_time = current + duration

        # Skip breaks
        skip = False
        for b in breaks:
            if max(current, b[0]) < min(next_time, b[1]):
                current = b[1]
                skip = True
                break

        if not skip:
            slots.append((current, next_time))
            current = next_time

    return slots


# ---------- GENERATE ----------
def generate_timetable(start, end, breaks, courses):
    timetable = {day: [] for day in DAYS}
    teacher_schedule = defaultdict(list)

    # Assign one teacher per course
    course_teacher = {
        c["name"]: random.choice(c["teachers"]) for c in courses
    }

    # ❗ Check impossible condition
    for c in courses:
        if c["weekly"] > len(DAYS):
            print(f"WARNING: {c['name']} has more classes than days!")

    # Create pool
    pool = []
    for c in courses:
        pool.extend([c] * c["weekly"])

    random.shuffle(pool)

    # Build slots per day
    all_slots = {}
    for day in DAYS:
        all_slots[day] = []

        for c in courses:
            slots = build_slots(start, end, breaks, c["duration"])
            for s in slots:
                all_slots[day].append((s[0], s[1], c["duration"]))

        random.shuffle(all_slots[day])

    # Assign classes
    for course in pool:
        teacher = course_teacher[course["name"]]
        duration = course["duration"]

        placed = False

        for day in DAYS:
            for slot in all_slots[day]:
                s, e, d = slot

                if d != duration:
                    continue

                conflict = False

                # ❗ Teacher conflict
                for t in teacher_schedule[teacher]:
                    if t[0] == day and max(s, t[1]) < min(e, t[2]):
                        conflict = True
                        break

                # ❗ Slot conflict + SAME SUBJECT SAME DAY restriction
                for item in timetable[day]:
                    # time overlap
                    if max(s, item["start"]) < min(e, item["end"]):
                        conflict = True
                        break

                    # ❗ IMPORTANT RULE
                    if item.get("course") == course["name"]:
                        conflict = True
                        break

                if not conflict:
                    timetable[day].append({
                        "course": course["name"],
                        "teacher": teacher,
                        "start": s,
                        "end": e
                    })

                    teacher_schedule[teacher].append((day, s, e))
                    placed = True
                    break

            if placed:
                break

    # Add breaks
    for day in DAYS:
        for b in breaks:
            timetable[day].append({
                "type": "BREAK",
                "start": b[0],
                "end": b[1]
            })

    # Sort by time
    for day in DAYS:
        timetable[day].sort(key=lambda x: x["start"])

    return timetable


# ---------- PRINT ----------
def print_timetable(timetable, title):
    print(f"\n===== {title} =====\n")

    # Collect all unique time slots
    all_slots = set()
    for day in DAYS:
        for item in timetable[day]:
            all_slots.add((item["start"], item["end"]))

    # Sort slots
    sorted_slots = sorted(list(all_slots))

    # Header
    print("DAY".ljust(12), end="")
    for s, e in sorted_slots:
        print(f"{to_time(s)}-{to_time(e)}".ljust(18), end="")
    print()

    print("-" * (12 + len(sorted_slots) * 18))

    # Rows
    for day in DAYS:
        print(day.ljust(12), end="")

        for s, e in sorted_slots:
            found = ""

            for item in timetable[day]:
                if item["start"] == s and item["end"] == e:
                    if item.get("type") == "BREAK":
                        found = "BREAK"
                    else:
                        found = f"{item['course']}({item['teacher']})"
                    break

            print(found.ljust(18), end="")

        print()

# ---------- MAIN ----------
def main():
    start, end, breaks, num_tables, courses = get_input()

    for i in range(num_tables):
        tt = generate_timetable(start, end, breaks, courses)
        print_timetable(tt, f"Timetable {i+1}")


if __name__ == "__main__":
    main()
