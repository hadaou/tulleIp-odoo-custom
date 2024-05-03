def rename_x_cat_image_to_cat_image(cr):
    """
    Rename the column x_cat_image to cat_image in product.template table.
    """
    # Check if column x_cat_image exists
    cr.execute("SELECT column_name FROM information_schema.columns WHERE table_name='product_template' AND column_name='x_cat_image'")
    if not cr.fetchone():
        # If x_cat_image does not exist, we can't do the migration, so return
        return

    # Rename x_cat_image to cat_image
    cr.execute(
        "ALTER TABLE product_template RENAME COLUMN x_cat_image TO cat_image")


def rebuild_internal_code_index(cr):
    """
    Rebuild the index for the internal_code field in product.product table.
    """
    # Drop the existing index for the internal_code field
    cr.execute("DROP INDEX IF EXISTS product_product_internal_code_index")

    # Create a new index for the internal_code field
    cr.execute(
        "CREATE INDEX IF NOT EXISTS product_product_internal_code_index ON product_product (internal_code)")


def migrate(cr, version):
    rename_x_cat_image_to_cat_image(cr)
