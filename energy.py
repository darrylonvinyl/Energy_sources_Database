""" Build a database of energy sources in the US. """


from argparse import ArgumentParser
import sqlite3
import sys


class EnergyDB:
    """Class used to create a database of energy sources in the U
    
    Attributes:
    filename (str): csv containing records of energy usage in the US.
    Example of the file:
        Year,State,Energy Source,Megawatthours
        1990,AK,Coal,510573.0
        1990,AK,Hydroelectric Conventional,974521.0
        1990,AK,Natural Gas,3466261.0
    
    """
    def __init__(self,filename):
        """The constructor for the EnergyDB class
        
        Attributes:
            conn (Connection): connection used to access sqlite db.
        
        Side effect:
            Creates an instance of EnergyDB, which includes a connection
            attribute. 
        """
        self.conn = sqlite3.connect('example.db')
        self.filename = self.read(filename)

    def __del__(self):
        """ Clean up the database connection. """
        try:
            self.conn.close()
        except:
            pass

    def read(self,filename):
        """Method to create a table in the DB, open the csv file, and update the
        db.

        Parameters:
            filename (str): csv containing records of energy usage in the US.

        Side effect:
            Creates a db table named production, opens the specified file with
            energy records, and updates the table with those records.
        """
        cursor = self.conn.cursor()
        # Added below line to destroy production DB on repeated script runs 
        cursor.execute('''DROP TABLE IF EXISTS production''')
        create_table_sql = '''CREATE TABLE production(
            year integer,
            state text,
            source text,
            mwh real
        )'''
        cursor.execute(create_table_sql)
        with open(filename) as f:
            for line in f.readlines()[1:]:
                x = line.split(sep=",")
                x[0] = int(x[0])
                x[3] = float(x[3])
                update_table_sql = '''INSERT INTO production VALUES(
                    ?,?,?,?
                )'''
                cursor.execute(update_table_sql,(x[0],x[1],x[2],x[3]))
        self.conn.commit()

    def production_by_source(self,source,year):
        """Method to find out the production of energy by its source.
        
        Attributes:
            source (str): source is a string from the Source column of
            energy.csv, for example, "Wind".
            year (int): year is an integer representing a year from
            energy.csv (1990–2017).

        Side effect:
            Get the value of the mwh column for each row that matches
            the specified source and year, and provides the sum.
        """
        cursor = self.conn.cursor()
        query_sql = "SELECT mwh FROM production WHERE source=? AND year=?"
        cursor.execute(query_sql,(source,year))
        results = cursor.fetchall()
        total_mwh = 0.0
        if results:
            for record in results:
                total_mwh =+ record[0]
        return total_mwh

def main(filename):
    """ Build a database of energy sources and calculate the total production
    of solar and wind energy.
    
    Args:
        filename (str): path to a CSV file containing four columns:
            Year, State, Energy Source, Megawatthours.
    
    Side effects:
        Writes to stdout.
    """
    e = EnergyDB(filename)
    sources = [("solar", "Solar Thermal and Photovoltaic"),
               ("wind", "Wind")]
    for source_lbl, source_str in sources:
       print(f"Total {source_lbl} production in 2017: ",
             e.production_by_source(source_str, 2017))


def parse_args(arglist):
    """ Parse command-line arguments. """
    parser = ArgumentParser()
    parser.add_argument("file", help="path to energy CSV file")
    return parser.parse_args(arglist)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    main(args.file)
