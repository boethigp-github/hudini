"""create trigger to generate api key after user creation

Revision ID: 7ccad2d03809
Revises: 6bbad1d03808
Create Date: 2024-09-14 10:34:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7ccad2d03809'
down_revision = '6bbad1d03808'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Activate the pgcrypto extension to use gen_random_bytes()
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

    # Check if the table 'api_keys' exists, create if not
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'api_keys') THEN
            CREATE TABLE api_keys (
                id UUID DEFAULT uuid_generate_v4() NOT NULL,
                "user" UUID NOT NULL,
                key VARCHAR(64) NOT NULL,
                created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                PRIMARY KEY (id),
                FOREIGN KEY("user") REFERENCES users (uuid) ON DELETE CASCADE
            );
        END IF;
    END $$;
    """)

    # Create a function to generate an API key for a user after insertion
    op.execute("""
    CREATE OR REPLACE FUNCTION create_api_key_for_user()
    RETURNS TRIGGER AS $$
    DECLARE
        new_api_key TEXT;
    BEGIN
        -- Generate a new API key using pgcrypto's gen_random_bytes()
        new_api_key := encode(gen_random_bytes(32), 'hex');
        
        -- Insert the new API key into the api_keys table
        INSERT INTO api_keys("user", key, created) 
        VALUES (NEW.uuid, new_api_key, now());
        
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # Create a trigger to call the function after a user is created
    op.execute("""
    CREATE TRIGGER trigger_create_api_key
    AFTER INSERT ON users
    FOR EACH ROW
    EXECUTE FUNCTION create_api_key_for_user();
    """)


def downgrade() -> None:
    # Drop the trigger and the function
    op.execute("DROP TRIGGER IF EXISTS trigger_create_api_key ON users;")
    op.execute("DROP FUNCTION IF EXISTS create_api_key_for_user();")

    # Drop the api_keys table if necessary
    op.execute("DROP TABLE IF EXISTS api_keys;")
