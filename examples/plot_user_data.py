"""
===================
choldgraf vs NelleV
===================

This short example shows the number of commits per user across time.
"""

from watchtower.handlers_ import GithubDatabase
import matplotlib.pyplot as plt

users = ['choldgraf', 'NelleV']

# Initialize the database
db = GithubDatabase()

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
    counts.plot(ax=ax, label=user.user, lw=3)
ax.set_title('Commits for users')
ax.xaxis.label.set(visible=False)
ax.legend()
plt.tight_layout()
plt.show()
