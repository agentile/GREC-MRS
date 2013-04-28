universe                = vanilla
executable              = /NLP_TOOLS/tool_sets/ace/latest/bin/ace 
log                     = condor.log
error                   = condor.error
output                  = /home2/agentile/LING575/src/ace.mrs.out
arguments               = "-g /NLP_TOOLS/tool_sets/ace/latest/erg-1111-x86-64-0.9.13.dat -1T /home2/agentile/LING575/src/sentences.out"
transfer_executable     = false
getenv                  = true
request_memory = 8*1024
queue
