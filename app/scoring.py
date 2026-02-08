def score_game(frames):
    running_total = 0

    for i in range(10):
        shots = frames[i]["shots"]

        # 10th frame: sum whatever is there
        if i == 9:
            frame_total = sum(convert_shots(shots))
            running_total += frame_total
            frames[i]["score"] = running_total
            continue

        # Strike
        if len(shots) == 1 and shots[0] == "X":
            bonus = next_two_shots(frames, i)
            frame_total = 10 + bonus
            running_total += frame_total
            frames[i]["score"] = running_total
            continue

        # Spare (already marked as "/")
        if len(shots) == 2 and shots[1] == "/":
            bonus = next_one_shot(frames, i)
            frame_total = 10 + bonus
            running_total += frame_total
            frames[i]["score"] = running_total
            continue

        # Detect numeric spare (e.g., 8 + 2)
        if len(shots) == 2:
            s1, s2 = shots
            if isinstance(s1, int) and isinstance(s2, int) and s1 + s2 == 10:
                frames[i]["shots"][1] = "/"
                bonus = next_one_shot(frames, i)
                frame_total = 10 + bonus
                running_total += frame_total
                frames[i]["score"] = running_total
                continue

        # Open frame
        frame_total = sum(convert_shots(shots))
        running_total += frame_total
        frames[i]["score"] = running_total

    return running_total


def convert_shots(shots):
    """Convert symbols to numeric values."""
    out = []
    for s in shots:
        if s == "X":
            out.append(10)
        elif s == "/":
            out.append(10 - out[-1])
        else:
            out.append(int(s))
    return out


def next_two_shots(frames, index):
    """Safely get the next two scoring shots."""
    collected = []

    for f in frames[index + 1:]:
        for s in f["shots"]:
            if s == "X":
                collected.append(10)
            elif s == "/":
                collected.append(10 - collected[-1])
            else:
                collected.append(int(s))

            if len(collected) == 2:
                return sum(collected)

    return sum(collected)


def next_one_shot(frames, index):
    """Safely get the next scoring shot."""
    for f in frames[index + 1:]:
        if not f["shots"]:
            continue

        s = f["shots"][0]

        if s == "X":
            return 10
        elif s == "/":
            return 10
        else:
            return int(s)

    return 0
