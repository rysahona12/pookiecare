# Product Images Directory

This directory stores all uploaded product images for the PookieCare e-commerce platform.

## Structure

```
media/
└── products/
    └── images/
        ├── product1.jpg
        ├── product2.png
        └── ...
```

## Usage

When uploading product images through the Django admin panel or API:
- Images will automatically be saved to this directory
- Django's ImageField handles file naming and storage
- Files can be accessed via URL: `/media/products/images/filename.ext`

## Supported Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)

## Best Practices

1. **Image Size**: Optimize images before uploading (recommended max: 2MB)
2. **Dimensions**: Recommended size: 800x800px for product images
3. **Format**: Use JPEG for photos, PNG for images with transparency
4. **Naming**: Django will handle unique naming automatically

## Development vs Production

- **Development**: Files are served by Django using `django.conf.urls.static`
- **Production**: Configure your web server (Nginx, Apache) to serve media files directly

## Notes

- This directory should be writable by the Django application
- In production, consider using cloud storage (AWS S3, Google Cloud Storage)
- Regularly backup this directory along with your database
