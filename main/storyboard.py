
#############################################################################
# Classes related to the CyPROM storyboard
#############################################################################

class Storyboard:

    #############################################################################
    # Generic constants

    # Program version
    CYPROM_VERSION = "0.1"

    # Module directories
    ACTIONS_DIR = "actions"
    TRIGGERS_DIR = "triggers"

    # Separator constants
    SEPARATOR1 = "-------------------------------------------------------------------------"
    SEPARATOR2 = "========================================================================="
    SEPARATOR3 = "#########################################################################"

    # Log constants
    #HEADER_TEMPLATE_LOW = "{0:^8} | {1:^10} | {2:^30}"
    #HEADER_TEMPLATE_BAR = "------------------------------------------------------"
    #LOG_TEMPLATE_LOW = "{0:^8} | {1:^10} | {2}"
    # The log templates below don't show time information
    HEADER_TEMPLATE_LOW = "{0:^13}|{1:^30}"
    HEADER_TEMPLATE_BAR = "-------------------------------------------"
    LOG_TEMPLATE_LOW = "{0:^13}| {1}"
    STEP_TEMPLATE = "  {0}: {1}"


    #############################################################################
    # Scenario constants

    # Top-level key
    SCENARIO_KEY = "scenario"

    # Scenario-level keys
    STEP_KEY = "step"
    LABEL_KEY = "label"
    TARGET_KEY = "target"

    ## Trigger keys
    TRIGGER_KEY = "trigger"
    MODULE_KEY = "module"
    NONE_VALUE = "none"
    SIGNAL_VALUE = "signal"
    TIMER_VALUE = "timer"
    TEST_VALUE = "test"

    ## Action keys
    ACTION_KEY = "action"
    #MODULE_KEY = "module"
    HINT_VALUE = "hint"
    MESSAGE_VALUE = "message"

    ## Outcome keys
    SUCCESS_KEY = "success"
    FAILURE_KEY = "failure"
    NEXT_KEY = "next"
    NEXT_SCENARIO_KEY = "next_scenario"
    POINTS_KEY = "points"
    LOOP_KEY = "loop"

    ### Predefined step ids
    STEP_FINISH = "FINISH"
    STEP_REPEAT = "REPEAT"
    STEP_COMPLETE = "COMPLETE"


    #############################################################################
    # Configuration file constants

    SCENARIO_DIRECTORY_KEY = "ScenarioDirectory"
    TARGET_FILE_KEY = "TargetInformation"
    INITIAL_SCORE_KEY = "InitialScore"

#    PUBLIC_SERVER_KEY = "PublicServer"
#    PUBLIC_PORT_KEY = "PublicPort"

#    LOG_MODE_KEY = "LogMode"

    MSF_SERVER = "MsfServer"
    MSF_PORT = "MsfPort"
    MSF_USER = "MsfUser"
    MSF_PASSWORD = "MsfPassword"
    MSF_SQL_PREFIX = "Msf"
    
    #############################################################################
    # Other constants

    # Default first scenario
    INITIAL_SCENARIO = "scenario.yml"

    # First step key in intermediate scenario files (.tmp/)
    FIRST_STEP_KEY = "first_step"

    # Service-related constants
    TCP_KEY = "tcp"
    UDP_KEY = "udp"
    PORT_KEY = "port"
    FUNCTION_KEY = "function"
    SSH_KEY = "ssh"
    HTTP_KEY = "http"
