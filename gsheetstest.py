"""
A simple example showing the GSheets adapter.
"""
from shillelagh.backends.apsw.db import connect
from shillelagh.lib import get_available_adapters

# show names of available adapters
print(get_available_adapters())

if __name__ == "__main__":
    connection = connect(":memory:",
    adapter_kwargs={
        "gsheetsapi": {
            "service_account_file": "credentials.json",
        },
    })

    cursor = connection.cursor()

    SQL = """
    SELECT *
    FROM "https://docs.google.com/spreadsheets/d/1_rN3lm0R_bU3NemO0s9pbFkY5LQPcuy1pscv8ZXPtg8/edit#gid=1648320094"
    """
    for row in cursor.execute(SQL):
        print(row)

    # SQL = """
    # SELECT *
    # FROM "https://docs.google.com/spreadsheets/d/1Giy-e7veuPPftBssjvYguJwxBD3pTooAJOeqdsxSTAw/edit#gid=0"
    # """

    # column_names = ["Time","Space","Light","Void","Life","Doom","Breath","Blood","Hope","Rage","Mind","Heart"]
    # row_names = ["Heir","Witch","Seer","Mage","Page","Knight","Rogue","Thief","Sylph","Maid","Bard","Prince"]
    
    
    # data = {}
    # for idz, row in enumerate(cursor.execute(SQL)):
    #     if idz < 12:
    #         rowdict = {}
    #         for idx, col in enumerate(row):
    #             rowdict[column_names[idx]] = col
    #         data[row_names[idz]] = rowdict

    # print(data["Maid"]["Light"])