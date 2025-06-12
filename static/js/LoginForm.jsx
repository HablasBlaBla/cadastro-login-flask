const { useState } = React;

function LoginForm() {
  const [nome, setNome] = useState('');
  const [senha, setSenha] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    // Submit the form data to the server
    const formData = new URLSearchParams();
    formData.append('nome', nome);
    formData.append('senha', senha);

    fetch('/entrar', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          // Show spinner and message before redirect
          setMessage({ type: 'success', text: 'Redirecionando...' });
          setLoading(false);
          const spinner = document.getElementById('loading-spinner');
          if (spinner) {
            spinner.style.display = 'flex';
            // Add animationend event listener to redirect immediately after animation
            spinner.addEventListener('animationend', () => {
              window.location.href = '/home';
            }, { once: true });
          } else {
            // Fallback redirect after 5 seconds if no animation event
            setTimeout(() => {
              window.location.href = '/home';
            }, 5000);
          }
        } else {
          setLoading(false);
          setMessage({ type: 'error', text: data.message || 'Login failed' });
        }
      })
      .catch(() => {
        setLoading(false);
        setMessage({ type: 'error', text: 'An error occurred' });
      });
  };

  return (
    <>
      {loading && (
        <div className="spinner-overlay" id="loading-spinner">
          <div className="loading-wide">
            <div className="l1 color"></div>
            <div className="l2 color"></div>
            <div className="e1 color animation-effect-light"></div>
            <div className="e2 color animation-effect-light-d"></div>
            <div className="e3 animation-effect-rot">X</div>
            <div className="e4 color animation-effect-light"></div>
            <div className="e5 color animation-effect-light-d"></div>
            <div className="e6 animation-effect-scale">*</div>
            <div className="e7 color"></div>
            <div className="e8 color"></div>
          </div>
          <div style={{ marginTop: '1rem', color: '#333', fontWeight: '600', fontSize: '1.2rem' }}>
            {message ? message.text : 'Redirecionando...'}
          </div>
        </div>
      )}
      <div className="login-container" style={{ filter: loading ? 'blur(2px)' : 'none', pointerEvents: loading ? 'none' : 'auto' }}>
        {message && !loading && (
          <div className={`alert ${message.type}`}>
            {message.text}
          </div>
        )}
        <form onSubmit={handleSubmit} className="login-form">
          <input
            type="text"
            name="nome"
            placeholder="Nome"
            value={nome}
            onChange={(e) => setNome(e.target.value)}
            required
          />
          <input
            type="password"
            name="senha"
            placeholder="Senha"
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
            required
          />
        <button type="submit" disabled={loading}>
          {loading ? (
            <>
              Entrando...
            </>
          ) : (
            'Entrar'
          )}
        </button>
        </form>
      </div>
    </>
  );
}
