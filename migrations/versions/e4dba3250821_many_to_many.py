"""many-to-many

Revision ID: e4dba3250821
Revises: e3a5a478920f
Create Date: 2022-07-19 12:58:19.581472

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4dba3250821'
down_revision = 'e3a5a478920f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('readers_books',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('reader_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['books.id'], ),
    sa.ForeignKeyConstraint(['reader_id'], ['readers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_readers_books_book_id'), 'readers_books', ['book_id'], unique=False)
    op.create_index(op.f('ix_readers_books_reader_id'), 'readers_books', ['reader_id'], unique=False)
    op.drop_index('ix_books_reader_id', table_name='books')
    op.drop_constraint('books_reader_id_fkey', 'books', type_='foreignkey')
    op.drop_column('books', 'reader_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('books', sa.Column('reader_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('books_reader_id_fkey', 'books', 'readers', ['reader_id'], ['id'])
    op.create_index('ix_books_reader_id', 'books', ['reader_id'], unique=False)
    op.drop_index(op.f('ix_readers_books_reader_id'), table_name='readers_books')
    op.drop_index(op.f('ix_readers_books_book_id'), table_name='readers_books')
    op.drop_table('readers_books')
    # ### end Alembic commands ###
