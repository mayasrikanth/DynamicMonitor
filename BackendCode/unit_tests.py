import Github


file_path = "requirements.txt"
g = Github(token)
repo = g.get_repo("MartinHeinz/python-project-blueprint")

file = repo.get_contents(file_path, ref="master")  # Get file from branch
data = file.decoded_content.decode("utf-8")  # Get raw string data
data += "\npytest==5.3.2"  # Modify/Create file

def push(path, message, content, branch, update=False):
    author = InputGitAuthor(
        "MartinHeinz",
        "martin7.heinz@gmail.com"
    )
    source = repo.get_branch("master")
    repo.create_git_ref(ref=f"refs/heads/{branch}", sha=source.commit.sha)  # Create new branch from master
    if update:  # If file already exists, update it
        contents = repo.get_contents(path, ref=branch)  # Retrieve old file to get its SHA and path
        repo.update_file(contents.path, message, content, contents.sha, branch=branch, author=author)  # Add, commit and push branch
    else:  # If file doesn't exist, create it
        repo.create_file(path, message, content, branch=branch, author=author)  # Add, commit and push branch

push(file_path, "Add pytest to dependencies.", data, "update-dependencies", update=True)
