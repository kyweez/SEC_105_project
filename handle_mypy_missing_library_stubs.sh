# This script is completly home-made.
# It's based on the Mypy doc : https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-library-stubs-or-py-typed-marker
#
# I tried to simply insert a py.typed file at the root folder of the package and MyPy was finally happy.
# However it's suggested to check sometimes if the following packages have improved to a PEP-561 package
# (or if they have a stub package - eg: https://pypi.org/project/grpc-stubs/)

# This function find and store in a variable the path of the project given as an argument
getProjectPathFolder(){
    TEMP_PROJECT_PATH=$(find -name $1 | grep tempFolder)
}


# Create a key : value dict where key == packageName and value == repository of the project
declare -A packageDict
packageDict['aiohttp_pydantic']='https://github.com/Maillol/aiohttp-pydantic'


# Launch the stubs pacakge generation
for key in "${!packageDict[@]}"; do
    echo ""
    echo "******************************************************************************"
    echo "Generation of the $key-stubs package to make MyPy happy"
    echo "******************************************************************************"

    echo ""
    echo "================================ Importing the repository ================================"
    echo "git clone ${packageDict[$key]} tempFolder"
    git clone "${packageDict[$key]}" tempFolder

    echo ""
    echo "============================= Getting the path of the project ============================"
    echo "getProjectPathFolder $key"
    getProjectPathFolder $key

    echo ""
    echo "================================= Generation of the stubs ================================"
    echo "stubgen -o tempFolder/out $TEMP_PROJECT_PATH"
    stubgen -o tempFolder/out $TEMP_PROJECT_PATH

    echo ""
    echo "========================== Moving the stubs into the virtualenv =========================="
    echo "mv tempFolder/out/$key venv/lib/python3.8/site-packages/$key-stubs"
    mv "tempFolder/out/$key" "venv/lib/python3.8/site-packages/$key-stubs"

    echo ""
    echo "================================= Deleting the tempFolder ================================"
    echo "rm -rf tempFolder"
    rm -rf tempFolder

    echo ""
    echo "******************************************************************************"
    echo "End of the $key-stubs package generation"
    echo "******************************************************************************"
done
