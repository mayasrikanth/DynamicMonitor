from github import Github
import os


remote_git_path = 'mayasrikanth/DynamicMonitor'

def test_push():
    token = os.getenv('GITHUB_PAT', '...')
    g = Github(token)
    repo = g.get_repo(remote_git_path)

    # Testing pushing file to github
    with open('biden_tsne6.csv', 'r') as file:
        content = file.read()
    git_file_path = 'BackendCode/biden_tsne6.csv'
    repo.create_file(git_file_path, "committing tsne", content, branch="main")
    print(git_file_path + ' CREATED')





if __name__ == '__main__':
    test_push()
