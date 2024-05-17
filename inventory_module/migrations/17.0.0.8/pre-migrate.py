def rename_pos_categ_id_to_pos_categ_ids(cr):
    """
    Rename the column pos_categ_id to pos_categ_ids in inventory.add_product_wizard table.
    """
    # Check if column pos_categ_id exists
    cr.execute("SELECT column_name FROM information_schema.columns WHERE table_name='inventory.add_product_wizard' AND column_name='pos_categ_id'")
    if not cr.fetchone():
        # If pos_categ_id does not exist, we can't do the migration, so return
        return

    # Rename pos_categ_id to pos_categ_ids
    cr.execute(
        "ALTER TABLE inventory.add_product_wizard RENAME COLUMN pos_categ_id TO pos_categ_ids")


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
    rename_pos_categ_id_to_pos_categ_ids(cr)
