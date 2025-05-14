import csv
import io
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum
from django.db import connection

from .models import Cel, Felajanlas
from .forms import FileUploadForm


def index(request):
    """Home page view"""
    return render(request, 'felajanlasok/index.html')


def upload_data(request):
    """View for handling file uploads"""
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Process cel file if provided
            if 'cel_file' in request.FILES:
                cel_file = request.FILES['cel_file']
                try:
                    # Read and process the file
                    decoded_file = cel_file.read().decode('utf-8')
                    io_string = io.StringIO(decoded_file)
                    reader = csv.DictReader(io_string, delimiter='\t')

                    # Count rows for feedback message
                    row_count = 0

                    # Process each row
                    for row in reader:
                        if row_count == 0:
                            row_count += 1
                            continue
                        # Convert 'civil' field from various formats to boolean
                        Cel.objects.create(
                            az=int(row['az']),
                            megnevezes=row['megnevezes'],
                            civil=int(row['civil'])
                        )
                        row_count += 1

                    messages.success(
                        request, f'{row_count} cél sikeresen feltöltve!')
                except Exception as e:
                    messages.error(
                        request, f'Hiba a cél adatok feldolgozása során: {str(e)}')

            # Process felajanlas file if provided
            if 'felajanlas_file' in request.FILES:
                felajanlas_file = request.FILES['felajanlas_file']
                try:
                    # _file Clear existing data first
                    Felajanlas.objects.all().delete()

                    # Read and process the file
                    decoded_file = felajanlas_file.read().decode('utf-8')
                    io_string = io.StringIO(decoded_file)
                    reader = csv.DictReader(io_string, delimiter='\t')

                    # Count rows for feedback message
                    row_count = 0

                    # Process each row
                    for row in reader:
                        # Handle date format
                        date_str = row['datum']
                        date_val = None

                        # Try different date formats
                        for fmt in ['%Y-%m-%d', '%Y.%m.%d', '%d.%m.%Y', '%Y/%m/%d']:
                            try:
                                date_val = datetime.strptime(
                                    date_str, fmt).date()
                                break
                            except ValueError:
                                continue

                        if not date_val:
                            # Skip this row if date couldn't be parsed
                            continue

                        # Only create if corresponding cel exists
                        try:
                            cel = Cel.objects.get(az=int(row['celaz']))
                            Felajanlas.objects.create(
                                datum=date_val,
                                celaz=cel,
                                szamlaaz=int(row['szamlaaz']),
                                osszeg=int(row['osszeg'])
                            )
                            row_count += 1
                        except (Cel.DoesNotExist, ValueError):
                            continue  # Skip if cel doesn't exist or data is invalid

                    messages.success(
                        request, f'{row_count} felajánlás sikeresen feltöltve!')
                except Exception as e:
                    messages.error(
                        request, f'Hiba a felajánlás adatok feldolgozása során: {str(e)}')

            return redirect('index')
    else:
        form = FileUploadForm()

    return render(request, 'felajanlasok/upload.html', {'form': form})


def task3_civil(request):
    """Task 3: List civil goals"""
    civil_goals = Cel.objects.filter(civil=True)
    context = {'civil_goals': civil_goals, 'title': '3. Civil célok'}
    return render(request, 'felajanlasok/task3_civil.html', context)


def task4_legtobb(request):
    """Task 4: List 99 Ft donations ordered by date and invoice ID"""
    donations_99 = Felajanlas.objects.filter(
        osszeg=99).order_by('datum', 'szamlaaz')
    context = {'donations': donations_99,
               'title': '4. 99 forintos felajánlások'}
    return render(request, 'felajanlasok/task4_legtobb.html', context)


def task5_marc4(request):
    """Task 5: Goals available for donation on March 4, 2008"""
    # Find donations made on that date to determine which goals were available
    date_to_check = datetime.strptime('2008-03-04', '%Y-%m-%d').date()
    goals_march4 = Cel.objects.filter(
        felajanlasok__datum=date_to_check
    ).distinct()

    context = {'goals': goals_march4, 'date': date_to_check,
               'title': '5. 2008. március 4-i célok'}
    return render(request, 'felajanlasok/task5_marc4.html', context)


def task6_hanyszor(request):
    """Task 6: Count of 10 Ft vs 90 Ft donations"""
    count_10 = Felajanlas.objects.filter(osszeg=10).count()
    count_90 = Felajanlas.objects.filter(osszeg=90).count()

    context = {
        'count_10': count_10,
        'count_90': count_90,
        'title': '6. 10 és 90 forintos felajánlások száma'
    }
    return render(request, 'felajanlasok/task6_hanyszor.html', context)


def task7_celonkent(request):
    """Task 7: Total donations by goal"""
    goals_with_totals = Cel.objects.annotate(total=Sum('felajanlasok__osszeg'))

    context = {
        'goals_with_totals': goals_with_totals,
        'title': '7. Célonkénti felajánlások'
    }
    return render(request, 'felajanlasok/task7_celonkent.html', context)


def task8_marcius(request):
    """Task 8: March report on non-civil goals"""
    # Get all donations for March for non-civil goals
    cursor = connection.cursor()

    # SQL query to get the specific data as required
    query = """
        SELECT 
            c.az,
            c.megnevezes,
            f.datum,
            f.szamlaaz,
            f.osszeg
        FROM 
            felajanlasok_felajanlas f
        JOIN 
            felajanlasok_cel c ON f.celaz_id = c.az
        WHERE 
            c.civil = 0
            AND strftime('%m', f.datum) = '03'
        ORDER BY 
            c.az, f.datum, f.szamlaaz
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    # Process data for the report
    report_data = {}
    for row in rows:
        goal_id, goal_name, date, invoice_id, amount = row

        if goal_id not in report_data:
            report_data[goal_id] = {
                'name': goal_name,
                'dates': {}
            }

        if date not in report_data[goal_id]['dates']:
            report_data[goal_id]['dates'][date] = []

        report_data[goal_id]['dates'][date].append({
            'invoice_id': invoice_id,
            'amount': amount
        })

    context = {
        'report_data': report_data,
        'title': '8. Márciusi kimutatás'
    }
    return render(request, 'felajanlasok/task8_marcius.html', context)
