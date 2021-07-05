import time
from models import engine, session, OperationalError, StatementError, wraps, Expiries, Probabilities

def mk_session(fun):
    def wrapper(*args, **kwargs):
        s = session()
        kwargs['session'] = s
        try:
            res = fun(*args, **kwargs)
        except Exception as e:
            s.rollback()
            s.close()
            raise e

        s.close()
        return res
    wrapper.__name__ = fun.__name__
    return wrapper


def retry_db(exceptions, n_retries=3, ival=1):
    def decorator(fun):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            exception_logged = False
            for r in range(n_retries):
                try:
                    return fun(*args, **kwargs)
                except exceptions as e:
                    if not exception_logged:
                        print(e)
                        exception_logged = True
                    else:
                        print("Retry #" + r + " after receiving exception.")

                    time.sleep(ival)
            return fun(*args, **kwargs)
        return wrapper
    return decorator


@retry_db((OperationalError, StatementError), n_retries=3)
@mk_session
def db_add_expiries(expiry, btc_price, rake_over, rake_under, session=None):
    try:
        insert_expiry = Expiries(
            expiry=expiry, btc_price=btc_price, rake_over=rake_over, rake_under=rake_under)
        session.add(insert_expiry)
        session.commit()
        return insert_expiry.idexpiries
    except Exception as e:
        print(e)
        return 0

@retry_db((OperationalError, StatementError), n_retries=3)
@mk_session
def db_add_probabilities(idexpiries, strike, over, under, session=None):
    try:
        insert_probability = Probabilities(
            idexpiries=idexpiries, strike=strike, over=over, under=under)
        session.add(insert_probability)
        session.commit()
        return insert_probability.idprobabilities
    except Exception as e:
        print(e)
        return 0
