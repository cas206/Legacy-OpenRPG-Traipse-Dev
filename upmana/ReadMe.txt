Welcome to Update Manager 0.6.7!!!

This is the first isntallment of Update Manager for the OpenRPG Virtual Game Table.  The package includes several files that allow users to install Update Manager as a package into other softwares that use Mercurial.  The package itself includes

updatemana.py ## The Update Manager
manfiest.py ## A clone of the Plugin Database file (plugindb.py) from the OpenRPG Project
validate.py ## Currently unused but it is here for future packaging, from the OpenRPG Project
xmltramp.py  ## From the OpenRPG Project
__init__.py ## So you can copy the upmana folder and import updatemana.py anywhere
tmp folder ## Used to protect files during a repository update
default_ignorelist.txt ## An empty txt, needed in case users cannot create their own ignorelist.txt
default_manifest.xml ## A nearly empty XML file.  Used to hold Update Manager information.

The code is incomplete in this version, but the pieces that are missing have notes in remarks on how to complete them.

So what can you do with Update Manager? If you have a project that you want to serve to users and user Mercurial as a way to deliver updates, Update Manager allows you to deliver those updates without the fear of creating a problem with user sentiment.  Users will be able to (when completed) access their Control tab and update to any revision or any branch that has been served via a repoistory.  Users also have the option to protect files from being overwritten during updates, or not update at all!

If you have a development team you can use Update Manager as a speedy way to surf through your branches and revisions.  
