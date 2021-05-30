# An Election System for WVSU CICT

## Key Features
- [x] Sign-up, Login, Logout
- [x] Voting
- [x] Results
- [ ] News and Updates - in progress, needs data from the results page
- [ ] Voting timer - in progress
- [ ] Profile page - in progress
- [ ] Change display picture - in progress

## How to run
1. Create a virtual environment in Python.
2. Activate python virtual environment with this command: `source venvFolderName/bin/activate` for linux users, kindly see documentation for windows users. Make sure you're on the right directory, specifically where your project folder is.
3. `pip install -r requirements.txt` to install flask packages
4. Install packages including: flask, bcrypt(for password hashing), pymongo(to make a connection, query and make changes in our MongoDB database)
5. `npm install` to install npm packages from `package.json`
6. `npm run develop:css` to build Tailwind for development (no purge) and start Flask application by running `python run.py`
7. When ready for production run  `npm run build:css` to prepare a purged CSS build for production
