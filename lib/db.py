"""database"""
from supabase import create_client, Client
from decouple import config

url: str = config("SUPABASE_URL")
key: str = config("SUPABASE_KEY")

class SupabaseDb():
    def __init__(self):
        self.db : Client = create_client(url, key)
        print("connected to supabase db")
    
    def insert(self, tablename: str, values: dict):
        try:
            response = self.db.table(tablename).insert(values).execute()
            return response.data
        except Exception as e:
            print("unable to insert data :{}".format(e.message))
            return None

    def select_all(self, tablename: str) -> list:
        try:
            response = self.db.table(tablename).select("*").execute()
            return response.data
        except Exception as e:
            print("unable to update data :{}".format(e))
            return None
    
    def select_with_filter(self, tablename: str, column: str, value: str) -> list:
        try:
            response = self.db.table(tablename).select("*").ilike(column, f"{value}%").execute()
            return response.data
        except Exception as e:
            print(f"unable to query data: {e}")

    def update(self, tablename: str, values: dict, id: int):
        try:
            response = self.db.table(tablename).update(values).eq("id", id).execute()
            return response.data
        except Exception as e:
            print("unable to update data :{}".format(e))
            return None
    
    def delete(self, tablename: str, id: int):
        try:
            response = self.db.table(tablename).delete().eq('id', id).execute()
            return response.data
        except Exception as e:
            print("unable to delete data :{}".format(e))
            return None

    def create_bucket(self, bucketname: str):
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
        """uploads an image and returns url to it"""
        try:
            response = self.db.storage.from_(bucket_name).upload(file_name, image_file.read())
            if response:
                # Get the public URL of the uploaded file
                public_url = self.db.storage.from_(bucket_name).get_public_url(file_name)
                return public_url
            else:
                return None
        except Exception as e:
            print(f"Unable to upload image to bucket: {e}")
            return None

    def delete_file_in_bucket(self, bucket_name: str, file_name: str):
        try:
            self.db.storage.from_(bucket_name).remove([file_name])
        except Exception as e:
            print("Error deleting file from :{} -> error: {}".format(bucket_name, e))
