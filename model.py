import os
from dotenv import load_dotenv
import psycopg2
from utils.printer import Printer
import time

# Load environment variables from .env
load_dotenv()

DB_PASSWORD = os.getenv("DB_PASSWORD")

class Model:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password=DB_PASSWORD,
            host='localhost',
            port=5432
        )

    def get_table_data(self, table_name):
        c = self.conn.cursor()
        Printer.print_info(table_name)
        c.execute(f'SELECT * FROM public."{table_name}"')
        result = c.fetchall()

        Printer.print_success(f"Successfull fetch from {table_name}: {result}", 5)

    def get_all_tables_data(self):
        Printer.print_success(f"get_all_tables_data tables", 5)
    
    def print_notices(self, notices):
        for notice in notices:
            _, _, notice_text = notice.partition(':')
            clean_notice = notice_text.strip()
            Printer.print_info(clean_notice)

    def insert_data(self, table_name, data):
        values = tuple(data.values())
        columns = ', '.join(data.keys())

        c = self.conn.cursor()

        if table_name == "Exhibit":

            query = """DO $$ BEGIN IF NOT EXISTS (SELECT "exhibit_id" FROM
                    "Exhibit" WHERE "exhibit_id" = {})
                    THEN INSERT INTO "Exhibit"("exhibit_id","exhibition_id","name","author","creation_date")
                    VALUES {}; RAISE NOTICE {}; ELSE RAISE NOTICE {}; END IF; END $$;
                    """.format(data['exhibit_id'], values,"'Successfully added to Exhibit table'", "'Error: This exhibit_id already exists!'")
            
        elif  table_name == "Exhibition":
            
            query = """
                DO $$ BEGIN
                    IF NOT EXISTS (
                        SELECT "exhibition_id" FROM "Exhibition"
                        WHERE "exhibition_id" = {}
                    ) THEN
                        INSERT INTO "Exhibition"({})
                        VALUES {};
                        RAISE NOTICE 'Successfully added new exhibition!';
                    ELSE
                        RAISE NOTICE 'Element with exhibition_id {} already exists in Exhibition!';
                    END IF;
                END $$;
            """.format(data['exhibition_id'], columns, values, data['exhibition_id'])
            
        elif  table_name == "Museum":

            query = """
                DO $$ BEGIN
                    IF NOT EXISTS (
                        SELECT "museum_id" FROM "Museum"
                        WHERE "museum_id" = {}
                    ) THEN
                        INSERT INTO "Museum"({})
                        VALUES {};
                        RAISE NOTICE 'Successfully added new museum!';
                    ELSE
                        RAISE NOTICE 'Element with museum_id {} already exists in Museum!';
                    END IF;
                END $$;
            """.format(data['museum_id'], columns, values, data['museum_id'])
        
        elif  table_name == "Director":

            query = """
                DO $$ BEGIN
                    IF NOT EXISTS (
                        SELECT "director_id" FROM "Director"
                        WHERE "director_id" = {}
                    ) THEN
                        INSERT INTO "Director"({})
                        VALUES {};
                        RAISE NOTICE 'Successfully added new director!';
                    ELSE
                        RAISE NOTICE 'Element with director_id {} already exists in Director!';
                    END IF;
                END $$;
            """.format(data['director_id'], columns, values, data['director_id'])

        try:
            c.execute(query)
            self.conn.commit()
            self.print_notices(self.conn.notices)
        except psycopg2.Error as e:
            self.conn.rollback()
            Printer.print_error(f"Error: {e}", 5)
            return
            
    def delete_data(self, table_name, id):
        c = self.conn.cursor()

        delete = ''

        if table_name == "Exhibit":
            delete = f'DELETE FROM "Exhibit" WHERE "exhibit_id" = {id};'
            
        elif  table_name == "Exhibition":
              delete = f'DELETE FROM "Exhibit" WHERE "exhibition_id" = {id};'\
                       f'DELETE FROM "Exhibition" WHERE "exhibition_id" = {id};'
            
        elif  table_name == "Museum":
            delete = f'DELETE FROM "Museum" WHERE "museum_id" = {id};'

        elif  table_name == "Director":
            delete = f'DELETE FROM "Director" WHERE "director_id" = {id};'

        try:
            c.execute(delete)
            self.conn.commit()

            if self.conn.notices:
                self.print_notices(self.conn.notices)
            else:
                Printer.print_success(f"Removed successfully from {table_name} element with id: {id}", 5)

        except psycopg2.Error as e:
            self.conn.rollback()
            Printer.print_error(f"Error: {e}", 5)
            return


    def update_data(self, table_name, id, new_data):
        c = self.conn.cursor()

        set_clause = ', '.join(f'"{key}" = \'{value}\'' for key, value in new_data.items())

        if table_name == "Exhibit":

            query = """DO $$ BEGIN IF EXISTS (SELECT "exhibit_id" FROM "Exhibit" WHERE "exhibit_id" = {})THEN
                     UPDATE "Exhibit" SET {} WHERE "exhibit_id" = {};
                     RAISE NOTICE 'Successfully updated Exhibit table';
                     ELSE RAISE NOTICE 'Element with exhibit_id {} does not exists in Exhibit!';
                     END IF; END $$;
                     """.format(id, set_clause, id, id)
            
        elif  table_name == "Exhibition":
            
            query = """DO $$ BEGIN IF EXISTS (SELECT "exhibition_id" FROM "Exhibition" WHERE "exhibition_id" = {})THEN
                     UPDATE "Exhibition" SET {} WHERE "exhibition_id" = {};
                     RAISE NOTICE 'Successfully updated Exhibition table';
                     ELSE RAISE NOTICE 'Element with exhibition_id {} does not exists in Exhibition!';
                     END IF; END $$;
                     """.format(id, set_clause, id, id)
            
        elif  table_name == "Museum":

            query = """DO $$ BEGIN IF EXISTS (SELECT "museum_id" FROM "Museum" WHERE "museum_id" = {})THEN
                     UPDATE "Museum" SET {} WHERE "museum_id" = {};
                     RAISE NOTICE 'Successfully updated Museum table';
                     ELSE RAISE NOTICE 'Element with museum_id {} does not exists in Museum!';
                     END IF; END $$;
                     """.format(id, set_clause, id, id)
        
        elif  table_name == "Director":

            query = """DO $$ BEGIN IF EXISTS (SELECT "director_id" FROM "Director" WHERE "director_id" = {})THEN
                     UPDATE "Director" SET {} WHERE "director_id" = {};
                     RAISE NOTICE 'Successfully updated Museum table';
                     ELSE RAISE NOTICE 'Element with director_id {} does not exists in Director!';
                     END IF; END $$;
                     """.format(id, set_clause, id, id)

        try:
            c.execute(query)
            self.conn.commit()
            self.print_notices(self.conn.notices)
        except psycopg2.Error as e:
            self.conn.rollback()
            Printer.print_error(f"Error: {e}", 5)
            return

    def select_data(self, selected_options):
        option_index = selected_options['option_index']
        data = selected_options['data']

        query = ''

        c = self.conn.cursor()


        if (option_index == 1):
            author_name = data['author_name']

            query = """
                SELECT ex.name as exhibit_name, e.name as exhibition_name, ex.author
                FROM "Exhibition" e
                LEFT JOIN "Exhibit" ex ON e.exhibition_id = ex.exhibition_id
                WHERE ex.author = '{}';
                """.format(author_name)
            
            try:
                begin = int(time.time() * 1000)
                c.execute(query)
                end = int(time.time() * 1000) - begin

                Printer.print_info(f"Request took {end} ms")

                records = c.fetchall()

                result_objects = []

                for record in records:
                    exhibit_name, exhibition_name, author = record
                    result_objects.append({
                        'exhibit_name': exhibit_name,
                        'exhibition_name': exhibition_name,
                        'author': author
                    })

                Printer.print_text('fetched {}'.format(result_objects))

            except psycopg2.Error as e:
                self.conn.rollback()
                Printer.print_error(f"Error: {e}", 5)
                return


        elif (option_index == 2):
            exhibition_id = data['exhibition_id']

            query = """
                    SELECT ex.author
                    FROM "Exhibition" e
                    LEFT JOIN "Exhibit" ex ON e.exhibition_id = ex.exhibition_id
                    WHERE e.exhibition_id = {}
                    GROUP BY ex.author;
                    """.format(exhibition_id)
            
            try:
                begin = int(time.time() * 1000)
                c.execute(query)
                end = int(time.time() * 1000) - begin

                Printer.print_info(f"Request took {end} ms")

                authors = c.fetchall()

                result_objects = []

                for author in authors:
                    author_name, = author
                    result_objects.append({
                        'author_name': author_name
                    })

                Printer.print_text('fetched authors: {}'.format(result_objects))

            except psycopg2.Error as e:
                self.conn.rollback()
                Printer.print_error(f"Error: {e}", 5)
                return
            
    def randomize_data(self, count):
        c = self.conn.cursor()

        c.execute("""
            DO $$
            DECLARE
                exhibition_id_seq INT;
                current_exhibition_id INT;
            BEGIN
                current_exhibition_id := COALESCE((SELECT max(exhibition_id) FROM "Exhibition"), 0) + 1;

                FOR exhibition_id_seq IN current_exhibition_id..current_exhibition_id + %s - 1
                LOOP
                    INSERT INTO "Exhibition" ("exhibition_id", "name", "start_date", "end_date")
                    VALUES (
                        exhibition_id_seq,
                        chr(trunc(65 + random()*26)::int)||chr(trunc(65 + random()*26)::int)||chr(trunc(65 + random()*26)::int),
                        current_date + (random() * interval '365 days'),
                        current_date + (random() * interval '365 days') + interval '30 days'
                    );
                END LOOP;
            END $$;
        """, (count,))

        c.execute("""
            DO $$
            DECLARE
                exhibit_id_seq INT;
                current_exhibit_id INT;
            BEGIN
                current_exhibit_id := COALESCE((SELECT max(exhibit_id) FROM "Exhibit"), 0) + 1;

                FOR exhibit_id_seq IN current_exhibit_id..current_exhibit_id + %s - 1
                LOOP
                    INSERT INTO "Exhibit" ("exhibit_id", "author", "creation_date", "name", "exhibition_id")
                    VALUES (
                        exhibit_id_seq,
                        chr(trunc(65 + random()*26)::int)||chr(trunc(65 + random()*26)::int)||chr(trunc(65 + random()*26)::int),
                        current_date - (random() * interval '365 days'),
                        chr(trunc(65 + random()*26)::int)||chr(trunc(65 + random()*26)::int)||chr(trunc(65 + random()*26)::int),
                        (SELECT "exhibition_id" FROM "Exhibition" ORDER BY random() LIMIT 1)  -- Select a random exhibition_id
                    );
                END LOOP;
            END $$;
        """, (count,))

        self.conn.commit()
