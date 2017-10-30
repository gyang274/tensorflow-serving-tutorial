## GitHub 

### Github Pages

```
# in master brach, push a sub-directory as gh-pages

$ git subtree push --prefix <sub-directory> origin gh-pages

# use gitbook, i often put documentation, e.g., source code of gitbook in 
# ./doc/src and ./doc/book.json, and compile the gitbook into ./doc/_book

$ git subtree push --prefix doc/_book origin gh-pages
```

### GitHub SSH Authentication

- add ssh public key into github account profile ssh keys

```
# copy key into github account profile

$ more ~/.ssh/id_rsa.pub
```

- set remote origin url into a form that supports ssh

```
# git+ssh://git@github.com/username/reponame.git
# note: NOT https://github.com/username/reponame.git

# add remote
$ git remote add origin git+ssh://git@github.com/username/reponame.git

# inspect remote
$ git remote show origin

# reset the repo url
$ git remote set-url origin git+ssh://git@github.com/username/reponame.git
```
