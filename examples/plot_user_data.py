from watchtower.handlers_ import GithubDatabase
import matplotlib.pyplot as plt
import os

users = ['choldgraf', 'Carreau', 'NelleV']
auth = os.environ['GITHUB_API']

# Initialize the database
db = GithubDatabase(auth=auth)

# Update users and print the db
for user in users:
    db.update(user)
print(db)

# Load the data for plotting
users = [db.load(user) for user in users]

# Now plot pushes each day
fig, ax = plt.subplots(figsize=(10, 5))
for user in users:
    counts = user.PushEvent.resample('D').count().iloc[:, 0]
    counts.plot(ax=ax, label=user.user, lw=3, alpha=.5)
ax.set_title('Commits for users')
ax.xaxis.label.set(visible=False)
ax.legend()
plt.tight_layout()
plt.show()
