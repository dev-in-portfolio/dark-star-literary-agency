# Dark Star Literary Agency

Static multi-page public-facing website for Dark Star Literary Agency, the creative home of Ambrose Caspian Vale and the Lulu & Ellie Adventures.

## Site Structure

- `index.html` - homepage and brand gateway
- `agency.html` - Dark Star Literary Agency identity page
- `ambrose-caspian-vale.html` - author page
- `lulu-and-ellie.html` - flagship universe page
- `library.html` - library landing and navigation hub
- `parents-teachers.html` - parent and teacher trust page
- `contact.html` - public contact page

### Series Pages

- `series/lulu-and-ellie-adventures.html`
- `series/mystery-tails.html`
- `series/creature-rescue-club.html`
- `series/backyard-academy.html`
- `series/go-to-camp.html`
- `series/lulu-and-ellie-in-space.html`
- `series/bedtime-adventures.html`

### Learning Pages

- `learning/phonics-path.html`
- `learning/write-and-wag.html`
- `learning/cursive-club.html`
- `learning/learning-club.html`

### Book Pages

- `books/` contains one page for every listed book in the catalog, plus public-facing write-ups for the deepest catalog layer.

## Shared Styling

- `styles.css` contains the shared layout, color palette, cards, buttons, status badges, purchase placeholder treatment, and responsive behavior.
- Every page uses the same header and footer pattern.

## Public Language

The site uses customer-facing terms such as:

- series
- collections
- book lines
- learning lines
- companion books
- library
- universe
- storyworld
- books
- adventures

## Purchase Placeholders

- Individual series, learning line, and book pages include a `Purchase Links Coming Soon` section with a clear placeholder button.
- Purchase links are not faked and are only added when real official purchase options are ready.
- Placeholder buttons use `href="#"`, `aria-disabled="true"`, and the `disabled-link` class.

## Contact

Public contact email:

`darstarliteraryagency@gmail.com`
