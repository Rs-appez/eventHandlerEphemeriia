def write_log(msg):
    with open("log.txt", "a") as f:
        f.write("\n")
        f.write(msg)
        f.write("\n")
        f.write("-" * 100)