# -*- coding: utf-8 -*-
__title__   = "Help"
__doc__     = """Version = 1.1
Date     = 25.10.2026
________________________________________________________________
Description:

EN - Shows the contact email and the link to the documentation of the JFS tools.
ES - Muestra el correo de contacto y el enlace a la documentación de las herramientas JFS.
________________________________________________________________
Last Updates:

- [25.10.2026] v1.1 Link to the documentation on GitHub."""
__author__  = "Javier Fidalgo Saeta"
__helpurl__ = "https://github.com/javi-arch/jfs-pyrevit-tools"


# IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS

from pyrevit import forms


# MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN


msg = ("EN - For any questions or issues that may arise with the tools, please do not hesitate to contact the following email address:\n\njavier.fidalgo.saeta@gmail.com\n\n"
       "Documentation: https://github.com/javi-arch/jfs-pyrevit-tools\n\n\n"
       "ES - Para cualquier pregunta o problema que pueda surgir con las herramientas, por favor no dude en ponerse en contacto con la siguiente dirección de correo electrónico:\n\njavier.fidalgo.saeta@gmail.com\n\n"
       "Documentación: https://github.com/javi-arch/jfs-pyrevit-tools")

forms.alert(msg, exitscript=True)
