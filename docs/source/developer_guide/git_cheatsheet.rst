GIT cheatsheet
==============

Excellent and thorough documentation on how to use GIT can be found online on
the official GIT documentation or by searching on Google. We summarize here
only a set of commands that may be useful.

Switch to another branch
------------------------
You can switch to another branch with::

  git checkout newbranchname
  
and you can see the list of checked-out branches, and the one you are in,
with::

  git branch
  
(or ``git branch -a`` to see also the list of remote branches).

.. _git_associate_local_remote_branch:

Associate a local and remote branch
-----------------------------------

To tell GIT to always push a local branch (checked-out) to a remote branch
called ``remotebranchname``, check out the correct local branch and then
do::

  git push --set-upstream origin remotebranchname

From now on, you will just need to run ``git push``. This will create a new 
entry in ``.git/config`` similar to::

  [branch "localbranchname"]
    remote = origin
    merge = refs/heads/remotebranchname
    
Branch renaming
---------------
To rename a branch `locally`, from ``oldname`` to ``newname``::

  git checkout oldname
  git branch -m oldname newname
  
If you want also to rename it remotely, you have to create a new branch and
then delete the old one. One way to do it, is first editing ``~/.git/config`` 
so that the branch points to the new remote name, changing
``refs/heads/oldname`` to ``refs/heads/newname`` in the correct section::

[branch "newname"]
    remote = origin
    merge = refs/heads/newname
    
Then, do a::

  git push origin newname
  
to create the new branch, and finally delete the old one with::

  git push origin :oldname
  
(notice the : symbol).
Note that if you are working e.g. on BitBucket, there may be a filter to
disallow the deletion of branches (check in the repository settings, and 
then under "Branch management"). Moreover, the "Main branch" (set in the
repository settings, under "Repository details") cannot be deleted. 

Create a new (lightweight) tag
------------------------------
If you want to create a new tag, e.g. for a new version, and you have checked
out the commit that you want to tag, simply run::

  git tag TAGNAME
  
(e.g., ``git tag v0.2.0``). Afterwards, remember to push the tag to the remote
repository (otherwise it will remain only local)::

  git push --tags
  
Create a new branch from a given tag
------------------------------------
This will create a new ``newbranchname`` branch starting from tag ``v0.2.0``::

  git checkout -b newbranchname v0.2.0
  
Then, if you want to push the branch remotely and have git remember
the association::

  git push --set-upstream origin remotebranchname 
   
(for the meaning of --set-upsteam see the section
:ref:`git_associate_local_remote_branch` above).

Disallow a branch deletion, or committing to a branch, on BitBucket
-------------------------------------------------------------------
You can find these settings in the repository settings of the web interface, and 
then under "Branch management".

.. note:: if you commit to a branch (locally) and then discover that you cannot
  push (e.g. you mistakenly committed to the master branch), you can remove
  your last commit using::
    
    git reset --hard HEAD~1
    
  (this removes one commit only, and you should have no local modifications;
  if you do it, be sure to avoid losing your modifications!)
  
  