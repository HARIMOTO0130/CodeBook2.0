# Create a simple favicon.ico file
# This script creates a basic 32x32 pixel favicon with a blue background and white text

# Define the favicon path
$faviconPath = "public/favicon.ico"

# Create a simple favicon using .NET
Add-Type -AssemblyName System.Drawing

# Create a 32x32 bitmap
$bitmap = New-Object System.Drawing.Bitmap(32, 32)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)

# Set background color (blue)
$graphics.Clear([System.Drawing.Color]::FromArgb(52, 152, 219))

# Set text properties
$font = New-Object System.Drawing.Font("Arial", 14, [System.Drawing.FontStyle]::Bold)
$brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
$format = New-Object System.Drawing.StringFormat
$format.Alignment = [System.Drawing.StringAlignment]::Center
$format.LineAlignment = [System.Drawing.StringAlignment]::Center

# Draw "CB" text for CodeBook
$graphics.DrawString("CB", $font, $brush, 16, 16, $format)

# Save the bitmap as favicon.ico
$bitmap.Save($faviconPath, [System.Drawing.Imaging.ImageFormat]::Icon)

# Clean up
$graphics.Dispose()
$bitmap.Dispose()
$font.Dispose()
$brush.Dispose()

Write-Host "Favicon created successfully at: $faviconPath"
