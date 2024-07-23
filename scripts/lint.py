import subprocess


def main():
    subprocess.run(["black", "."])
    subprocess.run(["isort", "."])
    subprocess.run(["flake8", "src/."])
