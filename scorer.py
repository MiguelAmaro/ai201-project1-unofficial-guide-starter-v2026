def judge(question, expects, answer, results):
    for result in results:
        if expects.lower() in result.text.lower():
            return True

    return False