import { useEffect, useMemo, useState } from 'react'
import { Search, ShoppingBag, Tag, ShieldCheck, MessageCircle, ArrowRight, Plus, LogIn, LogOut, UserRound, X, Sparkles, Package, BriefcaseBusiness, HeartHandshake, Menu } from 'lucide-react'
import api, { money } from './api'

const fallbackCategories = [
  { name: 'Electronics', description: 'Gadgets, phones and more', kind: 'product', slug: 'electronics' },
  { name: 'Fashion', description: 'Clothing, shoes and accessories', kind: 'product', slug: 'fashion' },
  { name: 'Home & Furniture', description: 'Make your space yours', kind: 'product', slug: 'home-and-furniture' },
  { name: 'Beauty & Personal Care', description: 'Everyday essentials', kind: 'product', slug: 'beauty-and-personal-care' },
  { name: 'Books & Education', description: 'Learn something new', kind: 'both', slug: 'books-and-education' },
  { name: 'Sports & Fitness', description: 'Gear up and get moving', kind: 'product', slug: 'sports-and-fitness' },
  { name: 'Grocery', description: 'Daily needs, better value', kind: 'product', slug: 'grocery' },
  { name: 'Services', description: 'Skills and services nearby', kind: 'service', slug: 'services' }
]
const categoryIcons = ['◈', '✳', '⌂', '✦', '▤', '⌁', '✿', '↗']

function App() {
  const [categories, setCategories] = useState(fallbackCategories)
  const [listings, setListings] = useState([])
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('')
  const [kind, setKind] = useState('')
  const [notice, setNotice] = useState('')
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('bb_user') || 'null') } catch { return null }
  })
  const [modal, setModal] = useState('')
  const [authMode, setAuthMode] = useState('login')
  const [auth, setAuth] = useState({ name: '', email: '', password: '', role: 'buyer' })
  const [listingForm, setListingForm] = useState({ title: '', description: '', listing_type: 'product', category_id: '', price: '', condition: 'new', location: '', quantity: 1, negotiable: true })
  const [offer, setOffer] = useState({ listing_id: '', amount: '', message: '' })
  const [busy, setBusy] = useState(false)

  const fetchData = async () => {
    setLoading(true)
    try {
      const [c, l] = await Promise.all([api.get('/categories/'), api.get('/listings/')])
      if (c.data?.length) setCategories(c.data)
      setListings(l.data?.items || [])
    } catch {
      setNotice('API not connected yet. Start the FastAPI backend to load live marketplace data.')
    } finally { setLoading(false) }
  }
  useEffect(() => { fetchData() }, [])

  const filtered = useMemo(() => listings.filter(item => {
    const matchText = !query || `${item.title} ${item.description}`.toLowerCase().includes(query.toLowerCase())
    const matchCategory = !category || item.category_id === category
    const matchKind = !kind || item.listing_type === kind
    return matchText && matchCategory && matchKind
  }), [listings, query, category, kind])

  const submitAuth = async (e) => {
    e.preventDefault(); setBusy(true); setNotice('')
    try {
      const endpoint = authMode === 'login' ? '/auth/login' : '/auth/register'
      const payload = authMode === 'login'
        ? { email: auth.email, password: auth.password }
        : auth
      const { data } = await api.post(endpoint, payload)
      localStorage.setItem('bb_token', data.access_token)
      localStorage.setItem('bb_user', JSON.stringify(data.user))
      setUser(data.user); setModal(''); setAuth({ name: '', email: '', password: '', role: 'buyer' })
      setNotice(`Welcome${data.user?.name ? `, ${data.user.name}` : ''}! You are signed in.`)
    } catch (err) { setNotice(err.response?.data?.detail || 'Could not sign in. Check the API and your details.') }
    finally { setBusy(false) }
  }

  const logout = () => {
    localStorage.removeItem('bb_token'); localStorage.removeItem('bb_user'); setUser(null)
    setNotice('You have signed out.')
  }

  const submitListing = async (e) => {
    e.preventDefault(); setBusy(true)
    try {
      await api.post('/listings/', { ...listingForm, price: Number(listingForm.price), quantity: Number(listingForm.quantity) })
      setModal(''); setNotice('Your listing has been published.'); setListingForm({ title: '', description: '', listing_type: 'product', category_id: '', price: '', condition: 'new', location: '', quantity: 1, negotiable: true }); fetchData()
    } catch (err) { setNotice(err.response?.data?.detail || 'Could not publish listing. Sign in and check the form.') }
    finally { setBusy(false) }
  }

  const submitOffer = async (e) => {
    e.preventDefault(); setBusy(true)
    try {
      await api.post('/offers/', { ...offer, amount: Number(offer.amount) })
      setModal(''); setNotice('Offer sent to the seller.'); setOffer({ listing_id: '', amount: '', message: '' })
    } catch (err) { setNotice(err.response?.data?.detail || 'Could not send offer. Please sign in first.') }
    finally { setBusy(false) }
  }

  const openOffer = (item) => {
    if (!user) { setAuthMode('login'); setModal('auth'); return }
    setOffer({ listing_id: item.id, amount: item.price, message: '' }); setModal('offer')
  }

  return (
    <div className="app-shell">
      <div className="topline"><span>THE MARKETPLACE WHERE EVERY PRICE IS A STARTING POINT</span><span>Made for smarter shopping in India <span className="flag">✦</span></span></div>
      <header className="navbar">
        <a className="brand" href="#" onClick={() => { setCategory(''); setKind('') }}>
          <span className="brand-mark"><Tag size={21}/></span><span>Bargain<span className="brand-accent">Baazaar</span><small>DISCOVER · NEGOTIATE · SAVE</small></span>
        </a>
        <nav className="nav-links"><a href="#categories">Categories</a><a href="#marketplace">Explore deals</a><a href="#how">How it works</a></nav>
        <div className="nav-actions">
          {user ? <><span className="user-chip"><UserRound size={15}/>{user.name}</span><button className="btn-ghost" onClick={logout}><LogOut size={16}/> Sign out</button></> : <button className="btn-ghost" onClick={() => { setAuthMode('login'); setModal('auth') }}><LogIn size={16}/> Sign in</button>}
          <button className="btn-primary small" onClick={() => user ? setModal('listing') : (setAuthMode('login'), setModal('auth'))}><Plus size={16}/> Sell an item</button>
        </div>
      </header>

      {notice && <div className="notice"><span>{notice}</span><button onClick={() => setNotice('')} aria-label="Dismiss"><X size={16}/></button></div>}

      <main>
        <section className="hero">
          <div className="hero-copy">
            <div className="eyebrow"><Sparkles size={14}/> A BETTER WAY TO BUY & SELL</div>
            <h1>Good finds.<br/><em>Better deals.</em></h1>
            <p className="hero-text">Discover products and services you love. Make an offer, find your price, and deal directly with the seller.</p>
            <div className="hero-buttons"><a className="btn-primary" href="#marketplace">Explore marketplace <ArrowRight size={17}/></a><button className="btn-outline" onClick={() => user ? setModal('listing') : (setAuthMode('register'), setModal('auth'))}>Start selling</button></div>
            <div className="hero-proof"><span><ShieldCheck size={16}/> Buyer-first experience</span><span><HeartHandshake size={16}/> Prices worth discussing</span></div>
          </div>
          <div className="hero-art">
            <div className="orb orb-one"></div><div className="orb orb-two"></div>
            <div className="deal-card">
              <div className="deal-top"><span className="live-dot"></span> THE ART OF THE DEAL <span className="deal-spark">✦</span></div>
              <div className="product-visual"><div className="headphone"><div className="headband"></div><div className="ear ear-left"></div><div className="ear ear-right"></div></div></div>
              <div className="deal-product"><div><b>Wireless headphones</b><small>Seller's asking price</small></div><strong>₹4,999</strong></div>
              <div className="offer-line"><span>Your offer</span><b>₹3,800</b><span className="offer-pill">-24%</span></div>
              <div className="deal-footer"><span>Seller accepted your offer</span><span className="accepted">✓ Deal!</span></div>
            </div>
            <div className="float-note note-one"><span className="note-icon">₹</span><span><b>Your price, your call</b><small>Negotiation made simple</small></span></div>
            <div className="float-note note-two"><span className="note-icon purple">↗</span><span><b>List in minutes</b><small>Reach ready-to-buy people</small></span></div>
          </div>
          <div className="hero-bottom"><span>01 / DISCOVER</span><span>02 / MAKE AN OFFER</span><span>03 / GET THE DEAL</span></div>
        </section>

        <section className="trust-strip"><div><b>01</b><span>Browse your way</span></div><div><b>02</b><span>Negotiate directly</span></div><div><b>03</b><span>Agree on a fair price</span></div><div><b>04</b><span>Complete the deal</span></div></section>

        <section className="section categories-section" id="categories">
          <div className="section-heading"><div><div className="eyebrow dark">FIND YOUR SOMETHING</div><h2>Shop by <em>category.</em></h2></div><p>From everyday essentials to specialist services,<br/>your next great find is a few clicks away.</p></div>
          <div className="category-grid">
            {categories.map((cat, i) => <button className={`category-tile ${category === cat.id ? 'selected' : ''}`} key={cat.id || cat.slug || cat.name} onClick={() => { setCategory(cat.id || ''); setKind(cat.kind === 'service' ? 'service' : '') ; document.getElementById('marketplace')?.scrollIntoView({ behavior: 'smooth' }) }}>
              <span className="category-symbol">{categoryIcons[i % categoryIcons.length]}</span><span className="category-name">{cat.name}</span><span className="category-description">{cat.description}</span><ArrowRight className="category-arrow" size={17}/>
            </button>)}
          </div>
        </section>

        <section className="market-section" id="marketplace">
          <div className="section-heading market-heading"><div><div className="eyebrow">FRESH FROM THE MARKET</div><h2>Find your next <em>great deal.</em></h2></div><span className="market-count">{filtered.length} LISTINGS</span></div>
          <div className="filters">
            <label className="search-box"><Search size={18}/><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search products, services and more..."/></label>
            <select value={kind} onChange={e => setKind(e.target.value)}><option value="">All listings</option><option value="product">Products</option><option value="service">Services</option></select>
            <select value={category} onChange={e => setCategory(e.target.value)}><option value="">All categories</option>{categories.filter(c => c.id).map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</select>
            {(category || kind || query) && <button className="clear-filter" onClick={() => { setCategory(''); setKind(''); setQuery('') }}>Clear</button>}
          </div>
          {loading ? <div className="empty-state"><div className="loader"></div><p>Loading the marketplace…</p></div> :
            filtered.length ? <div className="listing-grid">{filtered.map(item => <article className="listing-card" key={item.id}>
              <div className="listing-image">{item.image_urls?.[0] ? <img src={item.image_urls[0]} alt={item.title}/> : <div className="image-placeholder">{item.listing_type === 'service' ? <BriefcaseBusiness size={38}/> : <Package size={38}/>}<span>{item.listing_type === 'service' ? 'SERVICE' : 'GOOD FIND'}</span></div>}
                <span className="type-tag">{item.listing_type}</span>{item.negotiable && <span className="negotiable-tag">Open to offers</span>}</div>
              <div className="listing-info"><span className="listing-category">{categories.find(c => c.id === item.category_id)?.name || 'Marketplace'}</span><h3>{item.title}</h3><p>{item.description}</p><div className="listing-bottom"><strong>{money(item.price)}</strong><button onClick={() => openOffer(item)}>Make offer <ArrowRight size={14}/></button></div></div>
            </article>)}</div> : <div className="empty-state"><ShoppingBag size={34}/><h3>No listings here just yet</h3><p>Try another category or check back soon. New finds are added regularly.</p><button className="btn-outline dark-outline" onClick={() => { setCategory(''); setKind(''); setQuery('') }}>View all listings</button></div>}
        </section>

        <section className="how-section" id="how"><div className="how-intro"><div className="eyebrow">SIMPLE BY DESIGN</div><h2>Shopping should<br/>be a <em>conversation.</em></h2><p>We believe the best deals happen when buyers and sellers can talk openly and agree on a price that works.</p></div><div className="how-steps"><div className="how-step"><span>01</span><div><h3>Find what you want</h3><p>Explore categories and discover products or services from sellers.</p></div></div><div className="how-step"><span>02</span><div><h3>Make your move</h3><p>Send a fair offer. The seller can accept, decline or counter.</p></div></div><div className="how-step"><span>03</span><div><h3>Make it a deal</h3><p>Agree on the final price and move towards checkout.</p></div></div></div></section>
      </main>

      <footer><a className="brand footer-brand" href="#"><span className="brand-mark"><Tag size={19}/></span><span>Bargain<span className="brand-accent">Baazaar</span><small>DISCOVER · NEGOTIATE · SAVE</small></span></a><span>Better deals begin with a conversation.</span><span>© 2026 Bargain Baazaar</span></footer>

      {modal && <div className="modal-backdrop" onMouseDown={e => e.target === e.currentTarget && setModal('')}><div className="modal">
        <button className="modal-close" onClick={() => setModal('')}><X size={19}/></button>
        {modal === 'auth' && <><div className="modal-eyebrow">WELCOME TO THE BAazAAR</div><h2>{authMode === 'login' ? 'Good to see you.' : 'Create your account.'}</h2><p className="modal-sub">Sign in to make offers, save finds and list your own.</p><form onSubmit={submitAuth}>
          {authMode === 'register' && <><label>Your name<input required minLength="2" value={auth.name} onChange={e => setAuth({...auth, name:e.target.value})} placeholder="Full name"/></label><label>Account type<select value={auth.role} onChange={e => setAuth({...auth, role:e.target.value})}><option value="buyer">Buyer</option><option value="seller">Seller</option></select></label></>}
          <label>Email address<input required type="email" value={auth.email} onChange={e => setAuth({...auth, email:e.target.value})} placeholder="you@example.com"/></label><label>Password<input required minLength="8" type="password" value={auth.password} onChange={e => setAuth({...auth, password:e.target.value})} placeholder="At least 8 characters"/></label><button className="btn-primary full" disabled={busy}>{busy ? 'Please wait…' : authMode === 'login' ? 'Sign in' : 'Create account'} <ArrowRight size={16}/></button></form><p className="switch-auth">{authMode === 'login' ? 'New to Bargain Baazaar?' : 'Already have an account?'} <button onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}>{authMode === 'login' ? 'Create account' : 'Sign in'}</button></p></>}
        {modal === 'listing' && <><div className="modal-eyebrow">PUT IT ON THE MARKET</div><h2>Create a listing.</h2><p className="modal-sub">Give buyers the details they need to make an offer.</p><form onSubmit={submitListing}>
          <label>Listing title<input required minLength="3" value={listingForm.title} onChange={e => setListingForm({...listingForm,title:e.target.value})} placeholder="What are you selling?"/></label>
          <div className="form-row"><label>Type<select value={listingForm.listing_type} onChange={e => setListingForm({...listingForm,listing_type:e.target.value,category_id:''})}><option value="product">Product</option><option value="service">Service</option></select></label><label>Category<select required value={listingForm.category_id} onChange={e => setListingForm({...listingForm,category_id:e.target.value})}><option value="">Choose category</option>{categories.filter(c => c.id && (c.kind === 'both' || c.kind === listingForm.listing_type)).map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</select></label></div>
          <div className="form-row"><label>Asking price (₹)<input required type="number" min="1" step="1" value={listingForm.price} onChange={e => setListingForm({...listingForm,price:e.target.value})} placeholder="e.g. 2500"/></label><label>Quantity<input type="number" min="1" value={listingForm.quantity} onChange={e => setListingForm({...listingForm,quantity:e.target.value})}/></label></div>
          <label>Description<textarea required minLength="10" rows="3" value={listingForm.description} onChange={e => setListingForm({...listingForm,description:e.target.value})} placeholder="Describe the condition, features or service details…"/></label>
          <label>Location<input value={listingForm.location} onChange={e => setListingForm({...listingForm,location:e.target.value})} placeholder="City, state"/></label>
          <label className="check-label"><input type="checkbox" checked={listingForm.negotiable} onChange={e => setListingForm({...listingForm,negotiable:e.target.checked})}/> Open to price negotiation</label>
          <button className="btn-primary full" disabled={busy}>{busy ? 'Publishing…' : 'Publish listing'} <ArrowRight size={16}/></button></form></>}
        {modal === 'offer' && <><div className="modal-eyebrow">LET'S FIND A FAIR PRICE</div><h2>Make an offer.</h2><p className="modal-sub">The seller can accept, reject or send a counteroffer.</p><form onSubmit={submitOffer}><label>Your offer (₹)<input required type="number" min="1" value={offer.amount} onChange={e => setOffer({...offer,amount:e.target.value})}/></label><label>Message (optional)<textarea rows="3" value={offer.message} onChange={e => setOffer({...offer,message:e.target.value})} placeholder="Add a note for the seller…"/></label><button className="btn-primary full" disabled={busy}>{busy ? 'Sending…' : 'Send offer'} <ArrowRight size={16}/></button></form></>}
      </div></div>}
    </div>
  )
}

export default App
