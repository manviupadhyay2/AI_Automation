from django.db import models
import re
import pandas as pd
# from django.forms import LogFileUploadForm
from django import forms


class LogEntry(models.Model):
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField()
    http_method = models.CharField(max_length=50)
    url = models.URLField()
    http_status_code = models.CharField(max_length=3)
    user_agent = models.TextField()


    def sanitize(log_file,excel_file_path):
        data=[]
        with open(log_file,"r") as file:
            for line in file:
                parts= line.split()

                if len(parts)>=7:
                    ip=parts[0]
                    date_time=parts[3][1:]
                    method= parts[5][1:]
                    url=parts[6]
                    status_code=parts[8]
                    user_agent = ' '.join(parts[11:])

                data.append((ip, date_time, method, url, status_code, user_agent))

        columns=["IP", "Date-Time", "Method", "URL", "Status Code", "User Agent"]
        df=pd.DataFrame(data,columns=columns)

        df.to_excel(excel_file_path,index=False)



        print(f"Sanitized data saved to '{excel_file_path}'")
        return df

    
    def process_log_file(cls, log_file, excel_file_path):
        # Call the sanitize function to preprocess and save data
        df = sanitize(log_file, excel_file_path)

        # Iterate through the DataFrame and create LogEntry objects
        for index, row in df.iterrows():
            cls.objects.create(
                ip_address=row['IP'],
                timestamp=row['Date-Time'],
                http_method=row['Method'],
                url=row['URL'],
                http_status_code=row['Status Code'],
                user_agent=row['User Agent']
            )

        print(f"Log entries saved to the database.")

    def top_10_hits_hourly(df):
        hourly_hits = df.groupby(df['timestamp'].dt.hour)['timestamp'].count().nlargest(10)
        return hourly_hits

    # Task 2: Count total number of http codes
    def count_http_codes(df):
        http_code_counts = df['http_code'].value_counts()
        return http_code_counts

    # Task 3: Total hits per URL, find the URL with maximum hits
    def total_hits_per_url(df):
        url_hits = df['url'].value_counts()
        max_hit_url = url_hits.idxmax()
        return url_hits, max_hit_url

    # Task 4: Total hits per platform (android, IOS)
    def total_hits_per_platform(df):
        platform_hits = df['platform'].value_counts()
        return platform_hits

    # Task 5: Total hits per browser
    def total_hits_per_browser(df):
        browser_hits = df['browser'].value_counts()
        return browser_hits

    # Task 6: Traffic distribution on each site hourly basis
    def traffic_distribution_hourly(df):
        total_hours = df['hour'].nunique()
        traffic_distribution = df.groupby(['site', 'hour'])['timestamp'].count() / total_hours
        return traffic_distribution

    # Task 7: Total number of hits per hour (descending order)
    def total_hits_per_hour_descending(df):
        hourly_hits_descending = df.groupby(df['hour'])['timestamp'].count().sort_values(ascending=False)
        return hourly_hits_descending

    # Task 8: Plot graphs wherever possible
    def plot_graph(data, x_label, y_label, title):
        plt.figure(figsize=(12, 6))
        sns.barplot(x=data.index, y=data.values)
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.show()
        

    def main_menu():
        print("\nMenu:")
        print("1. Top 10 hits hourly basis")
        print("2. Count total number of HTTP codes")
        print("3. Total hits per URL")
        print("4. Total hits per platform")
        print("5. Total hits per browser")
        print("6. Traffic distribution on each site hourly basis")
        print("7. Total number of hits per hour (descending order)")
        print("8. Exit")


    def menu_choice():
        while True:
            main_menu()
            choice = input("Enter your choice (1-8): ")

            if choice == '1':
                top_10_hits_hourly(df)
                break
            elif choice == '2':
                count_http_codes(df)
                break
            elif choice == '3':
                total_hits_per_url(df)
                break
            elif choice == '4':
                total_hits_per_platform(df)
                break
            elif choice == '5':
                total_hits_per_browser(df)
                break
            elif choice == '6':
                traffic_distribution_hourly(df)
                break
            elif choice == '7':
                total_hits_per_hour_descending(df)
                break
            else:
                print("Invalid choice. Please select a valid option (1-8).")

    def main():
        sanitize("C:\\Users\\apoor\\Downloads\\log\\log_file.log","C:\\Users\\apoor\\Downloads\\log_file_analysis.xlsx")
        main_menu()
        menu_choice()



   



        
