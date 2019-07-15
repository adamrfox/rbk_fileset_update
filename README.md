# rbk_fileset_update
A project to update a Rubrik NAS fileset to the "latest" directory

This project was written for a customer who wanted to update the include path of a NAS fileset on Rubrik based on the "latest" directory which were named with a date stamp (e.g. 2009_07_15_...).  So this script need to run from a NAS client that has the export/share mounted so it can find the latest path.  It will then update the include path to reflect the latest path so that when the next backup runs it will only search the latest path.  In many cases this will be done automatically with incremental backups but this was a specific requirement from the customer.

Assumptions
The script makes the following assumptions:

1. The export/share is defined on the Rubrik with an existing fileset with an include path.
2. The fileset has only 1 include path
3. The export/share is mounted on the host running the script and the path is accessible by the user running the script.
4. Ideally the SLA would bave a small window where backups would not occur and the script would run outside of that window.
5. The script uses the SDK library 'rubrik_cdm' so that must be installed.  This can be done via pip 'pip install rubrik_cdm'

Crednetials
With any API script, credentials are needed.  There are multiple ways to pass the Rubrik credentials to the script:

1. Edit the script with your specific credentials by setting the 'user' and 'password' variables.
2. Use the -c flag and specify as an arguement user:password on the commannd line.  Be careful of special characters grabbed by the shell.
3. Use the creds_encode script (https://github.com/adamrfox/creds_encode) to generate an obfuscated file with the credentials.  Use the array type 'rubrik'
4. If none of the above are done, the script will prompt the user for the credentials (the password will not be echoed).

NOTE: If the share has more than 1 fileset assinged to it, one will need to be specified by the user.  This can be done via the -f option or the script will prompt for it if needed.  If the share has only one fileset assigned, that fileset will be used automatically.

Usage:
<pre>
Usage: rbk_fileset_update [-hvD] [-c creds] [-f fileset] share path rubrik
-h | --help : Prints this message
-v | --verbose : Verbose mode.  Prints more information
-D| --debug : Debug mode.  Prints troubleshoting info (+ verbose mode)
-c | --creds= : Rubrik crednetials.  Either user:password or creds file
-f | --fileset= : Specify a fileset.  Needed if share has more than one assigned
share : The share as defined on the rubrk.  Format: host:share/path
path : The path to the share on the local machine
rubrik: The name or IP of the Rubrik
</pre>
