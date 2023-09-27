from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
import pyexcel as pe
# import pyexcel_xlsx


def download_summary(request):
    # Get the production statistics for the robots
    # You can customize this part based on your data structure and logic
    robot_statistics = [
        {"model": "R2", "version": "A1", "count": 11},
        {"model": "R2", "version": "B2", "count": 22},
        {"model": "R2", "version": "C3", "count": 33},
        {"model": "S1", "version": "D4", "count": 44},
        {"model": "S1", "version": "E5", "count": 55},
        {"model": "S1", "version": "F6", "count": 66},
    ]

    # Create a new Excel sheet
    sheet = pe.Sheet(
        [[stat["model"], stat["version"], stat["count"]] for stat in robot_statistics],
        name="Robot Summary"
    )

    # Add column headers to the first row of each sheet
    sheet.row += [["Модель", "Версия", "Количество за неделю"]]

    # Create a response with the Excel file
    response = HttpResponse(content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = "attachment; filename=robot_summary.xlsx"

    # Save the Excel sheet to the response
    sheet.save_to_memory("xlsx", response)

    return response
