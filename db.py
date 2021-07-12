import time
import pandas as pd
from models import Fixtures, engine, session, OperationalError, StatementError, wraps, Expiries, Probabilities

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
def db_add_probabilities(idexpiries, odds_id, strike, over, under, session=None):
    try:
        insert_probability = Probabilities(
            idexpiries=idexpiries, odds_id=odds_id, strike=strike, over=over, under=under)
        session.add(insert_probability)
        session.commit()
        return insert_probability.idprobabilities
    except Exception as e:
        print(e)
        return 0

@retry_db((OperationalError, StatementError), n_retries=3)
@mk_session
def db_get_expiry_data(expiry, odds_id, session=None):
    try:
        check_user = session.query(Expiries, Probabilities).with_entities(Expiries.expiry, Expiries.btc_price, Expiries.rake_over, Expiries.rake_under, Probabilities.odds_id, Probabilities.strike, Probabilities.over, Probabilities.under).filter(Expiries.expiry == expiry, Probabilities.odds_id == odds_id,Expiries.idexpiries == Probabilities.idexpiries).statement
        df = pd.read_sql(check_user, engine)
        if(df.empty):
            return None
        else:
            return df.to_json(orient="records")
    except Exception as e:
        print(e)
        return None


@retry_db((OperationalError, StatementError), n_retries=3)
@mk_session
def db_add_fixture(fixture_type, start_time, market_end_time, end_time, session=None):
    try:
        check_fixture = session.query(Fixtures).filter(Fixtures.fixtureType == fixture_type, Fixtures.startTime == start_time, Fixtures.marketEndTime == market_end_time, Fixtures.endTime == end_time).statement
        df = pd.read_sql(check_fixture, engine)
        if(df.empty):
            insert_fixture = Fixtures(fixtureType=fixture_type, startTime=start_time, marketEndTime=market_end_time, endTime=end_time)
            session.add(insert_fixture)
            session.commit()
            return insert_fixture.id

        return 0
        
    except Exception as e:
        print(e)
        return 0


@retry_db((OperationalError, StatementError), n_retries=3)
@mk_session
def db_get_fixture(fixture_time, session=None):
    try:
        check_fixture = session.query(Fixtures).with_entities(Fixtures.id, Fixtures.startTime, Fixtures.marketEndTime, Fixtures.endTime).filter(Fixtures.startTime > fixture_time).order_by(Fixtures.startTime.asc()).limit(1).statement
        df = pd.read_sql(check_fixture, engine)
        if(df.empty):
            return None
        else:
            return df.to_json(orient="records")
    except Exception as e:
        print(e)
        return None
