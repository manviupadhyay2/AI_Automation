from django.shortcuts import render, redirect
from .forms import LogFileUploadForm
from .models import LogEntry 
from django.http import HttpResponse
from django.template import loader

def upload_log_file(request):
    if request.method == 'POST':
        form = LogFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            log_file = form.cleaned_data['log_file']
            sanitized_data = LogEntry.sanitize(log_file)
            LogEntry.process_log_file(log_file)
            return redirect('analysis_results')
    else:
        form = LogFileUploadForm()
    return render(request, 'upload_log_file.html', {'form': form})



def index(request):
    
    template = loader.get_template('index.html')
    return HttpResponse(template.render())
    


# Implement other views for filter selection and analysis results display
def top_10_hits_hourly(df):
    hourly_hits = df.groupby(df['timestamp'].dt.hour)['timestamp'].count().nlargest(10)
    return render(request, 'reports/top_10_hits_hourly.html', {'data': data})

    # Task 2: Count total number of http codes
def count_http_codes(df):
    http_code_counts = df['http_code'].value_counts()
    return render(request, 'reports/count_http_codes.html', {'data': data})

    # Task 3: Total hits per URL, find the URL with maximum hits
def total_hits_per_url(df):
    url_hits = df['url'].value_counts()
    max_hit_url = url_hits.idxmax()
    return render(request, 'reports/total_hits_per_url.html', {'data': data})


    # Task 4: Total hits per platform (android, IOS)
def total_hits_per_platform(df):
    platform_hits = df['platform'].value_counts()
    return render(request, 'reports/total_hits_per_platform.html', {'data': data})

    # Task 5: Total hits per browser
def total_hits_per_browser(df):
    browser_hits = df['browser'].value_counts()
    return render(request, 'reports/total_hits_per_browser', {'data': data})

    # Task 6: Traffic distribution on each site hourly basis
def traffic_distribution_hourly(df):
    total_hours = df['hour'].nunique()
    traffic_distribution = df.groupby(['site', 'hour'])['timestamp'].count() / total_hours
    return render(request, 'reports/traffic_distribution_hourly.html', {'data': data})

    # Task 7: Total number of hits per hour (descending order)
def total_hits_per_hour_descending(df):
    hourly_hits_descending = df.groupby(df['hour'])['timestamp'].count().sort_values(ascending=False)
    return render(request, 'reports/total_hits_per_hour_descending.html', {'data': data})

    # Task 8: Plot graphs wherever possible
def plot_graph(data, x_label, y_label, title):
    plt.figure(figsize=(12, 6))
    sns.barplot(x=data.index, y=data.values)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()
        
