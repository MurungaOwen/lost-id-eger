"""database"""
from supabase import create_client, Client
from decouple import config

url: str = config("SUPABASE_URL")
key: str = config("SUPABASE_KEY")

class SupabaseDb():
    def __init__(self):
        """class constructor"""
        self.db : Client = create_client(url, key)
        print("connected to supabase db")
    
    def insert(self, tablename: str, values: dict):
        """inserts a row in our db"""
        try:
            response = self.db.table(tablename).insert(values).execute()
            if response.status_code == 409:
                raise ValueError("The ID has already been uploaded")
            else:
                return response.data
        except Exception as e:
            print("unable to insert data :{}".format(e.message))
            return None

    def select_all(self, tablename: str) -> list:
        """returns all rows"""
        try:
            response = self.db.table(tablename).select("*").execute()
            return response.data
        except Exception as e:
            print("unable to update data :{}".format(e))
            return None
    
    def select_with_filter(self, tablename: str, column: str, value: str) -> list:
        """returns matching rows to the value `uses ilike`"""
        try:
            response = self.db.table(tablename).select("*").ilike(column, f"{value}%").execute()
            return response.data
        except Exception as e:
            print(f"unable to query data: {e}")

    def update(self, tablename: str, values: dict, id: int):
        """updates table"""
        try:
            response = self.db.table(tablename).update(values).eq("id", id).execute()
            return response.data
        except Exception as e:
            print("unable to update data :{}".format(e))
            return None
    
    def delete(self, tablename: str, id: int):
        """delete a row or rows in database"""
        try:
            response = self.db.table(tablename).delete().eq('id', id).execute()
            return response.data
        except Exception as e:
            print("unable to delete data :{}".format(e))
            return None

    def create_bucket(self, bucketname: str):
        """creates a storage bucket if it doesnt exist"""
        try:
            return self.db.storage.create_bucket(bucketname)
        except Exception as e:
            print("unable to create a bucket :{}".format(e))
            return None
    
    def get_bucket(self, bucket_name: str):
        try:
            return self.db.storage.get_bucket(bucket_name)
        except Exception as e:
            print("unable to get bucket -> {} :{}".format(bucket_name, e))
            return None

    def upload_id_image(self, image_file, bucket_name: str, file_name: str):
        """Uploads an image and returns the URL to it."""
        image_file.seek(0) #if file was read reset seek pointer
        read_file = image_file.read()
        try:
            response = self.db.storage.from_(bucket_name).upload(file_name, read_file,{
            'contentType': image_file.content_type
            })
            if response:  # Check if the upload was successful
                public_url = self.db.storage.from_(bucket_name).get_public_url(file_name)       
                print("public url is {}".format(public_url))
                return public_url
            else:
                return None
        except Exception as e:
            return None

    def delete_file_in_bucket(self, bucket_name: str, file_name: str):
        try:
            self.db.storage.from_(bucket_name).remove([file_name])
        except Exception as e:
            print("Error deleting file from :{} -> error: {}".format(bucket_name, e))

