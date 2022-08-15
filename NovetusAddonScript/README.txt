Place masterScript.lua inside Novetus\addons\

Then open Novetus\addons\core\AddonLoader.lua

and change:
Addons = {"Utils", "ShadersCompatibility", "ServerWhitelist"}

to:
Addons = {"Utils", "ShadersCompatibility", "ServerWhitelist", "masterScript"}