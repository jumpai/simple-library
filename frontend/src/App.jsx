import { useCallback, useEffect, useMemo, useState } from "react";

const initialForm = { isbn: "", title: "", author: "" };

async function fetchJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  if (response.status === 204) {
    return null;
  }
  return response.json();
}

function StatusMessage({ status }) {
  if (!status?.message) {
    return <div className="status" />;
  }
  return <div className={`status ${status.type}`}>{status.message}</div>;
}

function CatalogTable({ books, onBorrow, onReturn, onDelete }) {
  if (!books.length) {
    return (
      <table>
        <thead>
          <tr>
            <th>ISBN</th>
            <th>Title</th>
            <th>Author</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td colSpan="5">No books yet.</td>
          </tr>
        </tbody>
      </table>
    );
  }

  return (
    <table>
      <thead>
        <tr>
          <th>ISBN</th>
          <th>Title</th>
          <th>Author</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {books.map((book) => {
          const statusText = book.available ? "Available" : `Borrowed by ${book.borrower}`;
          return (
            <tr key={book.isbn}>
              <td>{book.isbn}</td>
              <td>{book.title}</td>
              <td>{book.author}</td>
              <td>{statusText}</td>
              <td className="actions">
                <button onClick={() => onBorrow(book.isbn)} disabled={!book.available}>
                  Borrow
                </button>
                <button className="secondary" onClick={() => onReturn(book.isbn)} disabled={book.available}>
                  Return
                </button>
                <button className="danger" onClick={() => onDelete(book.isbn)}>
                  Delete
                </button>
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

function SummaryList({ items }) {
  if (!items.length) {
    return <p>No summary data yet.</p>;
  }
  return (
    <ul className="summary-list">
      {items.map((item) => (
        <li key={item.author}>
          {item.author} — {item.count} book(s)
        </li>
      ))}
    </ul>
  );
}

export default function App() {
  const [books, setBooks] = useState([]);
  const [summary, setSummary] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [availableOnly, setAvailableOnly] = useState(false);
  const [addStatus, setAddStatus] = useState(null);
  const [catalogStatus, setCatalogStatus] = useState(null);

  const catalogQuery = useMemo(() => (availableOnly ? "?available_only=true" : ""), [availableOnly]);

  const loadCatalog = useCallback(async () => {
    setCatalogStatus({ type: "info", message: "Loading catalog..." });
    try {
      const data = await fetchJson(`/books${catalogQuery}`);
      setBooks(data);
      setCatalogStatus({ type: "ok", message: "Catalog updated." });
    } catch (error) {
      setCatalogStatus({ type: "error", message: `Failed to load catalog: ${error.message}` });
    }
  }, [catalogQuery]);

  const loadSummary = useCallback(async () => {
    try {
      const data = await fetchJson("/summary");
      setSummary(data.items);
    } catch (error) {
      setSummary([]);
    }
  }, []);

  useEffect(() => {
    loadCatalog();
  }, [loadCatalog]);

  useEffect(() => {
    loadSummary();
  }, [loadSummary]);

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleAdd = async (event) => {
    event.preventDefault();
    if (!form.isbn.trim() || !form.title.trim() || !form.author.trim()) {
      setAddStatus({ type: "error", message: "Please fill in all fields." });
      return;
    }
    try {
      await fetchJson("/books", { method: "POST", body: JSON.stringify(form) });
      setAddStatus({ type: "ok", message: "Book added successfully." });
      setForm(initialForm);
      loadCatalog();
      loadSummary();
    } catch (error) {
      setAddStatus({ type: "error", message: `Failed to add book: ${error.message}` });
    }
  };

  const handleBorrow = async (isbn) => {
    const borrower = window.prompt("Borrower name:");
    if (!borrower) {
      return;
    }
    try {
      await fetchJson(`/books/${isbn}/borrow`, {
        method: "POST",
        body: JSON.stringify({ borrower })
      });
      loadCatalog();
      loadSummary();
    } catch (error) {
      setCatalogStatus({ type: "error", message: error.message });
    }
  };

  const handleReturn = async (isbn) => {
    try {
      await fetchJson(`/books/${isbn}/return`, { method: "POST" });
      loadCatalog();
      loadSummary();
    } catch (error) {
      setCatalogStatus({ type: "error", message: error.message });
    }
  };

  const handleDelete = async (isbn) => {
    const confirmed = window.confirm("Delete this book?");
    if (!confirmed) {
      return;
    }
    try {
      await fetchJson(`/books/${isbn}`, { method: "DELETE" });
      loadCatalog();
      loadSummary();
    } catch (error) {
      setCatalogStatus({ type: "error", message: error.message });
    }
  };

  return (
    <div className="app">
      <h1>Simple Library</h1>
      <p>Manage your personal catalog through a React interface backed by the REST API.</p>

      <section className="panel">
        <h2>Add a Book</h2>
        <form onSubmit={handleAdd}>
          <label>
            ISBN
            <input type="text" name="isbn" value={form.isbn} onChange={handleInputChange} autoComplete="off" required />
          </label>
          <label>
            Title
            <input type="text" name="title" value={form.title} onChange={handleInputChange} required />
          </label>
          <label>
            Author
            <input type="text" name="author" value={form.author} onChange={handleInputChange} required />
          </label>
          <div>
            <button type="submit">Add Book</button>
          </div>
        </form>
        <StatusMessage status={addStatus} />
      </section>

      <section className="panel">
        <div className="toolbar">
          <h2 style={{ marginBottom: 0 }}>Catalog</h2>
          <button type="button" onClick={loadCatalog}>
            Refresh
          </button>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={availableOnly}
              onChange={(event) => setAvailableOnly(event.target.checked)}
            />
            Show only available
          </label>
        </div>
        <CatalogTable books={books} onBorrow={handleBorrow} onReturn={handleReturn} onDelete={handleDelete} />
        <StatusMessage status={catalogStatus} />
      </section>

      <section className="panel">
        <div className="toolbar">
          <h2 style={{ marginBottom: 0 }}>Summary</h2>
          <button type="button" onClick={loadSummary}>
            Refresh Summary
          </button>
        </div>
        <SummaryList items={summary} />
      </section>
    </div>
  );
}
